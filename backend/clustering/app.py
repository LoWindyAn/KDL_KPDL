import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import schedule  
import time 
import yaml
import os
import logging
from datetime import datetime, timezone, timedelta

app = FastAPI()

# # Đọc file config để lấy thời gian interval
# def load_config():
#     config_path = os.path.join(os.path.dirname(__file__), "config/xxx.yml")
#     with open(config_path, "r") as f:
#         config = yaml.safe_load(f)
#     return config
# config = load_config()
# INTERVAL_MINUTES = config["schedule"]["interval_minutes"]

@app.get('/hello')
def hello ():
    return {"message":"Hello world"}







