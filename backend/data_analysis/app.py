import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import schedule  
import time 
import yaml
import os
import logging
from datetime import datetime, timezone, timedelta

app = FastAPI()

# Đọc file config để lấy thời gian interval
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/xxx.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
config = load_config()
INTERVAL_MINUTES = config["schedule"]["interval_minutes"]

logging.basicConfig(
    filename="logs/prediction_log.txt", 
    level=logging.INFO,
    format="%(message)s",  
)

def get_vn_time():
    vn_time = datetime.now(timezone.utc) + timedelta(hours=7)
    timestamp_str = vn_time.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_str

def log_event(event_type):
    logging.info(f"{get_vn_time()} - {event_type}")

@app.get('/correlation')
def correlation ():
    try:
        response = requests.get("http://database_api:8001/prices")
        if response.status_code == 200:
            data = response.json()["data"]
        df = pd.DataFrame(data)
        if 'time' in df.columns:
            df = df.drop(columns=['time'])
        correlation_matrix = df.corr().round(2).to_dict()
        body = {
            "data": correlation_matrix,
        }
        response = requests.post("http://database_api:8001/insert-correlation", json=body)
        log_event("Analysis Data correlation")
        return {"data": body}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")    


def schedule_data_insertion():
    schedule.every(INTERVAL_MINUTES).minutes.do(correlation)  
    while True:  
        schedule.run_pending()  
        time.sleep(1)  

@app.on_event("startup")
def on_startup():
    import threading
    threading.Thread(target=schedule_data_insertion, daemon=True).start()






