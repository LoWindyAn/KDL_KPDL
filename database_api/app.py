from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import connect, Error
from pydantic import BaseModel
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from typing import List
from datetime import datetime, timedelta
# Danh sách các nguồn được phép
origins = [
    "http://localhost:5173",  
    "http://localhost:80"
]

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

def get_db_connection():
    db_host = "database_service"  # Tên service trong docker-compose
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

@app.get("/hello")
def hello():
    return {"message": "Hello world"}

class CryptoPrice(BaseModel):
    time: str
    high_price: float
    low_price: float
    open_price: float
    close_price: float
    volume_btc: float
    volume_usd: float

# Endpoint POST để thêm dữ liệu
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

# Endpoint GET để lấy danh sách dữ liệu
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
def get_prices(start_date: str = None, days: int = 0):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)

    # Nếu không có start_date, lấy ngày hiện tại. Nếu có start_date, chuyển đổi nó thành kiểu datetime.
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    else:
        # Nếu không truyền start_date, lấy ngày hiện tại
        start_date = datetime.today()

    # Tính ngày kết thúc, dựa vào số ngày muốn lấy
    # Nếu `days` là 0, nghĩa là không có giới hạn về số ngày
    if days > 0:
        end_date = start_date - timedelta(days=days)
    else:
        # Nếu không có số ngày, lấy tất cả dữ liệu từ start_date
        end_date = datetime(2000, 1, 1)  # Chỉ lấy dữ liệu từ ngày trước đó

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
        return {"count":len(results), "data": results}
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    finally:
        cursor.close()
        connection.close()


@app.get("/healthcheck")
def mysql_healthcheck():
    try:
        # Kết nối thử đến MySQL
        connection = get_db_connection()
        connection.ping(reconnect=True)  # Kiểm tra kết nối
        
        # Đóng kết nối sau khi kiểm tra
        connection.close()
        
        # Trả về thông báo thành công nếu không có lỗi
        return {"status": "healthy", "message": "Database connection is healthy."}
    except Error as e:
        # Nếu có lỗi, trả về thông báo lỗi
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
    
# @app.get("/prices/resample")
# def get_resampled_prices(interval: str = Query(..., regex="^(hour|day|week|month)$")):
#     connection = get_db_connection()
#     if not connection:
#         raise HTTPException(status_code=500, detail="Database connection failed")
    
#     cursor = connection.cursor(dictionary=True)
#     try:
#         # Lấy dữ liệu từ cơ sở dữ liệu
#         cursor.execute("SELECT time, high_price, low_price, open_price, close_price, volume_btc, volume_usd FROM crypto_prices")
#         data = cursor.fetchall()

#         # Chuyển đổi dữ liệu thành DataFrame của Pandas
#         df = pd.DataFrame(data)
#         df['time'] = pd.to_datetime(df['time'])  # Chuyển cột 'time' thành kiểu datetime

#         # Kiểm tra giá trị của interval và thực hiện resample nếu cần
#         if interval == 'hour':
#             # Nếu interval là 'hour', không thực hiện resample, chỉ giữ nguyên dữ liệu
#             resampled_df = df
#         else:
#             # Định nghĩa các tần suất tương ứng cho các giá trị khác
#             interval_mapping = {
#                 'day': 'D',
#                 'week': 'W',
#                 'month': 'M'
#             }
#             freq = interval_mapping.get(interval)

#             # Resample data based on the selected interval and calculate required stats
#             resampled_df = df.resample(freq, on='time').agg({
#                 'high_price': 'max',        # Highest price in the period
#                 'low_price': 'min',         # Lowest price in the period
#                 'open_price': 'first',      # Open price (first value in the period)
#                 'close_price': 'last',      # Close price (last value in the period)
#                 'volume_btc': 'sum',        # Sum of volume in BTC
#                 'volume_usd': 'sum'         # Sum of volume in USD
#             })    

#         # Trả về kết quả
#         response_data = {
#             "periods": resampled_df.index.tolist(),
#             "high_prices": resampled_df['high_price'].tolist(),
#             "low_prices": resampled_df['low_price'].tolist(),
#             "open_prices": resampled_df['open_price'].tolist(),
#             "close_prices": resampled_df['close_price'].tolist(),
#             "volume_btc": resampled_df['volume_btc'].tolist(),
#             "volume_usd": resampled_df['volume_usd'].tolist()
#         }
        
#         return {"interval": interval, "data": response_data}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Database error: {e}")
#     finally:
#         cursor.close()
#         connection.close()
    
@app.get("/prices/resample")
def get_resampled_prices(interval: str = Query(..., regex="^(day|week|month)$")):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Mapping interval to SQL date format
        interval_mapping = {
            "day": "DATE(time)",
            "week": "DATE_FORMAT(time, '%Y-%u')",
            "month": "DATE_FORMAT(time, '%Y-%m')"
        }

        # Lấy format cho GROUP BY dựa trên interval
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
        # return {"interval": interval, "data": results}

          # Trả về mảng riêng biệt cho từng giá trị
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

@app.get("/prices/correlation")
def get_correlation_matrix():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT 
            high_price,
            low_price,
            open_price,
            close_price,
            volume_btc,
            volume_usd
        FROM crypto_prices;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(rows)
    correlation_matrix = df.corr().round(2).to_dict()  # Tính correlation và chuyển thành dict

    return {"correlation_matrix": correlation_matrix}


@app.get("/prices/trend")
def get_trend_data(interval: str = Query(..., regex="^(day|week|month)$")):
    connection = get_db_connection()  # Ensure you have the DB connection function defined somewhere
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Mapping interval to SQL date format
        interval_mapping = {
            "day": "DATE(time)",
            "week": "DATE_FORMAT(time, '%Y-%u')",
            "month": "DATE_FORMAT(time, '%Y-%m')"
        }
        group_by_format = interval_mapping.get(interval)
        if not group_by_format:
            raise HTTPException(status_code=400, detail="Invalid interval")

        # Query lấy dữ liệu resampled
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

        # Convert to DataFrame
        df = pd.DataFrame(rows)

        # Handle period column conversion based on the interval type
        try:
            # If interval is 'week', format the 'period' correctly for week data
            if interval == "week":
                df['period'] = pd.to_datetime(df['period'] + '-0', format='%Y-%U-%w')  # Correcting week format
            else:
                df['period'] = pd.to_datetime(df['period'])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error converting period: {e}")
        
        df.set_index('period', inplace=True)
        
        # Kiểm tra dữ liệu đủ dài để phân tích
        if len(df) < 2:
            raise HTTPException(status_code=400, detail="Not enough data for trend analysis")
        
        # Phân tích seasonal decomposition để lấy trend
        decomposition = seasonal_decompose(df['close_price'], model='additive', period=3)  # Adjust `period` as needed
        trend = decomposition.trend.dropna()
        seasonal = decomposition.seasonal.dropna()

        # Trả dữ liệu trend
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

# Schema nhận một danh sách các cluster
class ClustersCreate(BaseModel):
    clusters: List[ClusterCreate]


@app.post("/insert-cluster")
def add_clusters(clusters_data: ClustersCreate):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    try:
        # Xóa tất cả dữ liệu cũ trong bảng clusters
        cursor.execute("DELETE FROM clusters")
        
        # Chèn dữ liệu mới vào bảng clusters
        query = """
        INSERT INTO clusters (cluster_id, high_price, low_price, open_price, close_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Lặp qua các cluster trong dữ liệu và chèn vào cơ sở dữ liệu
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

    cursor = connection.cursor(dictionary=True)  # Trả kết quả dưới dạng dict
    try:
        query = "SELECT * FROM clusters"
        cursor.execute(query)
        clusters = cursor.fetchall()
        if not clusters:
            raise HTTPException(status_code=404, detail="No clusters found")

        # Xử lý kết quả và trả về JSON đúng định dạng
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
    # Kết nối cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Xoá tất cả dữ liệu cũ trong bảng prediction
        cursor.execute("DELETE FROM prediction")

        # Chèn dữ liệu mới vào bảng
        insert_query = "INSERT INTO prediction (time, predict) VALUES (%s, %s)"
        cursor.execute(insert_query, (prediction.time, prediction.predict))

        # Commit thay đổi vào cơ sở dữ liệu
        connection.commit()
        
        return {"message": "Prediction inserted successfully!"}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()

@app.get("/get-prediction")
async def get_prediction():
    # Kết nối cơ sở dữ liệu
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Lấy tất cả dữ liệu trong bảng prediction
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
