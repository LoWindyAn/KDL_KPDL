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

app = FastAPI()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/xxx.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
config = load_config()
INTERVAL_DAY = config["schedule"]["interval_cluster"]

logging.basicConfig(
    filename="logs/cluster_logs.txt", 
    level=logging.INFO,
    format="%(message)s",  
)

def get_vn_time():
    vn_time = datetime.now(timezone.utc) + timedelta(hours=7)
    timestamp_str = vn_time.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_str

def log_event(event_type):
    logging.info(f"{get_vn_time()} - {event_type}")

@app.get("/clustered_prices")
def clustered_prices():
    n_clusters = 20
    try:
        response = requests.get("http://database_api:8001/prices")
        response.raise_for_status()  
        raw_data = response.json()["data"]
        
        df = pd.DataFrame(raw_data)
        
        numeric_columns = ["high_price", "low_price", "open_price", "close_price",]
        df_features = df[numeric_columns]
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df["cluster_id"] = kmeans.fit_predict(df_features)
        
        cluster_summary = (
            df.groupby("cluster_id")[numeric_columns]
            .mean()
            .reset_index()
            .to_dict(orient="records")
        )

        body = {"clusters": cluster_summary}
        response = requests.post("http://database_api:8001/insert-cluster", json=body)
        response.raise_for_status()  
        
        log_event('CLUSTERED')
        return {"data":body}
      
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

def schedule_data_insertion():
    schedule.every(INTERVAL_DAY).days.do(clustered_prices)  

    while True:  
        schedule.run_pending()  
        time.sleep(1)  

@app.on_event("startup")
def on_startup():
    clustered_prices() 
    import threading
    threading.Thread(target=schedule_data_insertion, daemon=True).start()

    








