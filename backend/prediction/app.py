import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import schedule  
import time 
import yaml
import os
import logging
import numpy as np
from datetime import datetime, timezone, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib 
from pydantic import BaseModel

app = FastAPI()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/xxx.yml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
config = load_config()
INTERVAL_MIN = config["schedule"]["interval_minutes"]

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

def preprocess_data(data):
    df = pd.DataFrame(data)
    df["period"] = pd.to_datetime(df["period"])  
    df = df.sort_values(by="period")            

    features = []
    labels = []
    
    for i in range(7, len(df)-1):  
        feature = df.iloc[i-7:i][["open_price", "high_price", "low_price", "close_price"]].values.flatten()
        features.append(feature)
        
        labels.append(df.iloc[i+1]["close_price"])

    return np.array(features), np.array(labels)

@app.get("/train_model_prediction")
def train_model():
    try:
        print("Fetching data from API...")
        response = requests.get("http://database_api:8001/prices/resampling-day")
        if response.status_code == 200:
            data = response.json()["data"]

            log_event("Preprocessing data...")
            X, y = preprocess_data(data)
            log_event(f"Features shape: {X.shape}, Labels shape: {y.shape}")

            log_event("Splitting data into training and testing sets...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            log_event("Training model...")
            start_time = time.time()  
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            end_time = time.time()  

            log_event(f"Training took {end_time - start_time:.2f} seconds")

            score = model.score(X_test, y_test)
            log_event(f"Model R^2 score: {score:.2f}")

            model_path = "/app/models/price_prediction_model.pkl"
            joblib.dump(model, model_path)
            log_event(f"Model saved as '{model_path}'")
            return {"message": "Train models success"}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

class PricePredictionRequest(BaseModel):
    open_price: list[float]
    high_price: list[float]
    low_price: list[float]
    close_price: list[float]

def preprocess_input(data: PricePredictionRequest):
    features = np.array([
        data["open_price"] + data["high_price"] + data["low_price"] + data["close_price"]
    ])
    return features

@app.get("/prediction")
def prediction_price_next_day():
    try:
        response = requests.get("http://database_api:8001/prices/resampling-day?days=7")
        if response.status_code == 200:
            data = response.json()["data"]
            result = {
                    "open_price": [entry["open_price"] for entry in data],
                    "high_price": [entry["high_price"] for entry in data],
                    "low_price": [entry["low_price"] for entry in data],
                    "close_price": [entry["close_price"] for entry in data],
                }
            model = joblib.load("/app/models/price_prediction_model.pkl")
            features = preprocess_input(result)
            prediction = model.predict(features)
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            body = {"predict": prediction[-1], "time":tomorrow}
            response = requests.post("http://database_api:8001/insert-prediction", json=body)
            response.raise_for_status() 
            log_event(f"Prediction: '{prediction[-1]}' USD")
            return {"predict": prediction[-1], "time":tomorrow}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")    

def train_model_periodically():
    log_event("------ START TRAINING MODEL ------")
    train_model()
    log_event("------ END TRAINING ------")

def schedule_data_insertion():
    schedule.every(INTERVAL_MIN).minutes.do(prediction_price_next_day)  
    schedule.every(1).days.do(train_model_periodically)
    while True:  
        schedule.run_pending()  
        time.sleep(1)  

@app.on_event("startup")
def on_startup():
    prediction_price_next_day()
    import threading
    threading.Thread(target=schedule_data_insertion, daemon=True).start()




