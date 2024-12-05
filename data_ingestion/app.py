import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import schedule  # For scheduling tasks
import time  # For sleeping between task executions
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
INTERVAL_HOUR = config["schedule"]["interval_ingestion"]

# Thiết lập logging để ghi vào file log
logging.basicConfig(
    filename="logs/data_ingestion_logs.txt",  # File log để lưu thời gian
    level=logging.INFO,  # Chỉ ghi log ở mức INFO trở lên
    format="%(message)s",  # Định dạng log
)

def get_vn_time():
    vn_time = datetime.now(timezone.utc) + timedelta(hours=7)
    timestamp_str = vn_time.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp_str

def log_event(event_type):
    logging.info(f"{get_vn_time()} - {event_type} crawl data")

API_URL="https://min-api.cryptocompare.com/data/pricemultifull?fsyms=BTC&tsyms=USD"

@app.get("/current_raw_data")
def get_raw_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  
        data = response.json()
        raw_data =  data['RAW']['BTC']['USD']
        time = datetime.fromtimestamp(raw_data['LASTUPDATE'])
        time_gmt7 = time + timedelta(hours=7)

        # Lấy các giá trị cần thiết
        price_data = {
            "time": time_gmt7.isoformat(),
            "high_price": raw_data['HIGH24HOUR'],
            "low_price": raw_data['LOW24HOUR'],
            "open_price": raw_data['OPEN24HOUR'],
            "close_price": raw_data['PRICE'],
            "volume_btc": raw_data['VOLUME24HOUR'],
            "volume_usd": raw_data['VOLUME24HOURTO'],
        }
        return price_data
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

def insert_to_db():
    try:
        log_event("Start")  # Ghi thời gian bắt đầu
        data = get_raw_data()
        response = requests.post("http://database_api:8001/insert-db", json=data)
        response.raise_for_status()
        log_event("End")  # Ghi thời gian kết thúc
        return {"message: Insert success"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}
    

def schedule_data_insertion():
    schedule.every(INTERVAL_HOUR).hours.do(insert_to_db)  

    while True:  
        schedule.run_pending()  
        time.sleep(1)  

@app.on_event("startup")
def on_startup():
    logging.info(f"===> Application UP - {get_vn_time()}")
    insert_to_db() 
    import threading
    threading.Thread(target=schedule_data_insertion, daemon=True).start()

@app.on_event("shutdown")
def on_shutdown():
    logging.info(f"===> Application DOWN - {get_vn_time()}") 







