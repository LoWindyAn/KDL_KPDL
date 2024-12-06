from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import connect, Error
from pydantic import BaseModel
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from typing import List, Dict
from datetime import datetime, timedelta
origins = [
    "http://localhost:5173",  
    "http://localhost:80"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def get_db_connection():
    db_host = "database_service"  
    db_port = 3306
    db_user = "admin"
    db_password = "password123"
    db_name = "crypto_db"

    connection = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    return connection

@app.get("/healthcheck")
def mysql_healthcheck():
    try:
        connection = get_db_connection()
        connection.ping(reconnect=True)  
        
        connection.close()
        
        return {"status": "healthy", "message": "Database connection is healthy."}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

class CryptoPrice(BaseModel):
    time: str
    high_price: float
    low_price: float
    open_price: float
    close_price: float
    volume_btc: float
    volume_usd: float

@app.post("/insert-db")
def add_price(price_data: CryptoPrice):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO crypto_prices (time, high_price, low_price, open_price, close_price, volume_btc, volume_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            price_data.time,
            price_data.high_price,
            price_data.low_price,
            price_data.open_price,
            price_data.close_price,
            price_data.volume_btc,
            price_data.volume_usd
        ))
        connection.commit()
        return {"message": "Data inserted successfully"}
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()

@app.get("/prices")
def get_prices():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM crypto_prices ORDER BY time DESC")
        results = cursor.fetchall()
        return {"data": results}
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()

@app.get("/prices/resampling-day")
def get_prices_resampling_day(start_date: str = None, days: int = 0):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    else:
        start_date = datetime.today()

    if days == 0:
        end_date = datetime(2000, 1, 1)  
    else:
        end_date = start_date - timedelta(days=(days-1))

    query = f"""
        SELECT 
            DATE(time) AS period,
            AVG(high_price) AS high_price,
            AVG(low_price) AS low_price,
            AVG(open_price) AS open_price,
            AVG(close_price) AS close_price
        FROM crypto_prices
        WHERE time BETWEEN %s AND %s
        GROUP BY DATE(time)
        ORDER BY period ASC;
    """

    try:
        cursor.execute(query, (end_date, start_date))
        results = cursor.fetchall()
        return {"count": len(results), "data": results}
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()

@app.get("/prices/hour")
def get_price_to_dwm(interval: str = Query(..., regex="^(day|week|month)$")):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        current_time = datetime.now()

        if interval == "day":
            start_time = current_time - timedelta(days=1)  
        elif interval == "week":
            start_time = current_time - timedelta(weeks=1)  
        elif interval == "month":
            start_time = current_time - timedelta(days=30)  

        query = f"""
            SELECT *
            FROM crypto_prices
            WHERE time >= %s
            ORDER BY time ASC;
        """
        
        cursor.execute(query, (start_time,))
        results = cursor.fetchall()

        response_data = {
            "periods": [row['time'] for row in results],
            "high_prices": [row['high_price'] for row in results],
            "low_prices": [row['low_price'] for row in results],
            "open_prices": [row['open_price'] for row in results],
            "close_prices": [row['close_price'] for row in results],
            "volume_btc": [row['volume_btc'] for row in results],
            "volume_usd": [row['volume_usd'] for row in results]
        }
        
        return { "data": response_data }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    
    finally:
        cursor.close()
        connection.close()
    
@app.get("/prices/resample")
def get_price_to_dwm(interval: str = Query(..., regex="^(day|week|month)$")):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        interval_mapping = {
            "day": "DATE(time)",
            "week": "DATE_FORMAT(time, '%Y-%u')",
            "month": "DATE_FORMAT(time, '%Y-%m')"
        }

        group_by_format = interval_mapping.get(interval)
        if not group_by_format:
            raise HTTPException(status_code=400, detail="Invalid interval")
        
        query = f"""
            SELECT 
                {group_by_format} AS period,
                MAX(high_price) AS high_price,
                MIN(low_price) AS low_price,
                AVG(open_price) AS open_price,
                AVG(close_price) AS close_price,
                SUM(volume_btc) AS volume_btc,
                SUM(volume_usd) AS volume_usd
            FROM crypto_prices
            GROUP BY {group_by_format}
            ORDER BY period ASC;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        response_data = {
            "periods": [row['period'] for row in results],
            "high_prices": [row['high_price'] for row in results],
            "low_prices": [row['low_price'] for row in results],
            "open_prices": [row['open_price'] for row in results],
            "close_prices": [row['close_price'] for row in results],
            "volume_btc": [row['volume_btc'] for row in results],
            "volume_usd": [row['volume_usd'] for row in results]
        }
        
        return {"interval": interval, "data": response_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()

# Pydantic model for input data
class CorrelationData(BaseModel):
    data: Dict[str, Dict[str, float]]

# API endpoint
@app.post("/insert-correlation")
def insert_correlation(correlation_data: CorrelationData):
    try:
        connection = get_db_connection()
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()

        # Prepare SQL query for insertion
        insert_query = """
        INSERT INTO correlation_matrix (metric1, metric2, correlation)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE correlation = VALUES(correlation);
        """

        # Insert data into the database
        for metric1, correlations in correlation_data.data.items():
            for metric2, value in correlations.items():
                cursor.execute(insert_query, (metric1, metric2, value))
      
        cursor.close()
        connection.commit()
        return {"message": "Correlation data inserted successfully"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/correlation")
def get_correlation():
    try:
        # Kết nối với cơ sở dữ liệu
        connection = get_db_connection()
        
        if not connection:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()

        # Truy vấn dữ liệu từ bảng correlation_matrix
        cursor.execute("SELECT metric1, metric2, correlation FROM correlation_matrix")
        rows = cursor.fetchall()

        # Tái tạo cấu trúc JSON
        result = {}
        for metric1, metric2, correlation in rows:
            if metric1 not in result:
                result[metric1] = {}
            result[metric1][metric2] = correlation

        # Đóng kết nối
        cursor.close()
        connection.close()

        return {"correlation_matrix": result}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")



@app.get("/prices/trend")
def get_trend_data(interval: str = Query(..., regex="^(day|week|month)$")):
    connection = get_db_connection()  
    cursor = connection.cursor(dictionary=True)
    
    try:
        interval_mapping = {
            "day": "DATE(time)",
            "week": "DATE_FORMAT(time, '%Y-%u')",
            "month": "DATE_FORMAT(time, '%Y-%m')"
        }
        group_by_format = interval_mapping.get(interval)
        if not group_by_format:
            raise HTTPException(status_code=400, detail="Invalid interval")

        query = f"""
            SELECT 
                {group_by_format} AS period,
                AVG(close_price) AS close_price
            FROM crypto_prices
            GROUP BY {group_by_format}
            ORDER BY period ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        df = pd.DataFrame(rows)

        try:
            if interval == "week":
                df['period'] = pd.to_datetime(df['period'] + '-0', format='%Y-%U-%w') 
            else:
                df['period'] = pd.to_datetime(df['period'])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error converting period: {e}")
        
        df.set_index('period', inplace=True)
        
        if len(df) < 2:
            raise HTTPException(status_code=400, detail="Not enough data for trend analysis")
        
        decomposition = seasonal_decompose(df['close_price'], model='additive', period=3)  
        trend = decomposition.trend.dropna()
        seasonal = decomposition.seasonal.dropna()

        response_data = {
            "periods": trend.index.strftime('%Y-%m-%d').tolist(),
            "trend": trend.values.tolist(),
            "seasonal": seasonal.values.tolist()
        }

        return {"interval": interval, "data": response_data}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing trend data: {e}")
    finally:
        cursor.close()
        connection.close()


class ClusterCreate(BaseModel):
    cluster_id: int
    high_price: float
    low_price: float
    open_price: float
    close_price: float

class ClustersCreate(BaseModel):
    clusters: List[ClusterCreate]


@app.post("/insert-cluster")
def add_clusters(clusters_data: ClustersCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM clusters")
        
        query = """
        INSERT INTO clusters (cluster_id, high_price, low_price, open_price, close_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for cluster in clusters_data.clusters:
            cursor.execute(query, (
                cluster.cluster_id,
                cluster.high_price,
                cluster.low_price,
                cluster.open_price,
                cluster.close_price
            ))
        
        connection.commit()
        return {"message": "Cluster data inserted successfully"}
    
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    
    finally:
        cursor.close()
        connection.close()


@app.get("/clusters", response_model=dict)
def get_clusters():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)  
    try:
        query = "SELECT * FROM clusters"
        cursor.execute(query)
        clusters = cursor.fetchall()
        if not clusters:
            raise HTTPException(status_code=404, detail="No clusters found")

        response = {"clusters": clusters}
        return response

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")

    finally:
        cursor.close()
        connection.close()

class Prediction(BaseModel):
    time: datetime
    predict: float

@app.post("/insert-prediction")
async def insert_prediction(prediction: Prediction):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM prediction")

        insert_query = "INSERT INTO prediction (time, predict) VALUES (%s, %s)"
        cursor.execute(insert_query, (prediction.time, prediction.predict))

        connection.commit()
        
        return {"message": "Prediction inserted successfully!"}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()

@app.get("/get-prediction")
async def get_prediction():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM prediction")
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No predictions found")

        predictions = [{"time": row[0], "predict": row[1]} for row in result]
        return predictions[0]

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()
