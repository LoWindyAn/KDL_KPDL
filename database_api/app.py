from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import connect, Error
from pydantic import BaseModel
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
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
    """
    Endpoint trả về dữ liệu xu hướng (trend) dựa trên resample interval.
    - interval: "day", "week", hoặc "month"
    """
    connection = get_db_connection()
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

        # Chuyển đổi thành DataFrame để phân tích trend
        df = pd.DataFrame(rows)
        df['period'] = pd.to_datetime(df['period'])
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
