import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import schedule  
import time 
import yaml
import os
import logging
from datetime import datetime, timezone, timedelta
from sklearn.cluster import KMeans

origins = [
    "http://localhost:5173",  
    "http://localhost:80",
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

# Đọc file config để lấy thời gian interval
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/xxx.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
config = load_config()
INTERVAL_DAY = config["schedule"]["interval_cluster"]



@app.get('/hello')
def hello ():
    return {"message":"Hello world"}

def get_clustered_prices():
    # Call API để lấy dữ liệu
    n_clusters = 20
    try:
        response = requests.get("http://database_api:8001/prices")
        response.raise_for_status()  # Kiểm tra lỗi từ HTTP
        raw_data = response.json()["data"]
        
        # 2. Load dữ liệu vào pandas DataFrame
        df = pd.DataFrame(raw_data)
        
        # 3. Chọn các cột số liên quan đến giá cả để phân cụm
        numeric_columns = ["high_price", "low_price", "open_price", "close_price",]
        df_features = df[numeric_columns]
        
        # 4. Thực hiện phân cụm K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df["cluster_id"] = kmeans.fit_predict(df_features)
        
        # 5. Tổng hợp dữ liệu theo cụm
        cluster_summary = (
            df.groupby("cluster_id")[numeric_columns]
            .mean()
            .reset_index()
            .to_dict(orient="records")
        )

        body = {"clusters": cluster_summary}
        response = requests.post("http://database_api:8001/insert-cluster", json=body)
        response.raise_for_status()  # Kiểm tra lỗi nếu có từ API
        
        return {"message": "Cluster data inserted successfully"}
      
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

def schedule_data_insertion():
    schedule.every(INTERVAL_DAY).minutes.do(get_clustered_prices)  

    while True:  
        schedule.run_pending()  
        time.sleep(1)  

@app.on_event("startup")
def on_startup():
    # logging.info(f"===> Application UP - {get_vn_time()}")
    get_clustered_prices() 
    import threading
    threading.Thread(target=schedule_data_insertion, daemon=True).start()

    








