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
import joblib  # Để lưu mô hình


app = FastAPI()

# @app.get('/hello')
# def hello ():
#     return {"message":"Hello world"}
# Tạo thư mục lưu mô hình nếu chưa tồn tại
MODEL_DIR = "models"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def preprocess_data(data):
    # Chuyển đổi data thành DataFrame
    df = pd.DataFrame(data)
    df["period"] = pd.to_datetime(df["period"])  # Chuyển đổi cột period thành datetime
    df = df.sort_values(by="period")            # Sắp xếp theo thời gian

    # Tạo các đặc trưng (features) và nhãn (label)
    features = []
    labels = []
    
    # Thay vì bắt đầu từ 7, bạn sẽ tạo một cửa sổ di động (sliding window) kích thước 7
    # và sau đó dịch cửa sổ đó ra ngoài một ngày mỗi lần (gối lên nhau).
    for i in range(7, len(df)-1):  # Bắt đầu từ ngày 7, vì cần 7 ngày trước đó
        # Tạo đặc trưng cho 7 ngày trước đó (tạo một chuỗi các giá trị)
        feature = df.iloc[i-7:i][["open_price", "high_price", "low_price", "close_price"]].values.flatten()
        features.append(feature)
        
        # Nhãn là giá đóng cửa của ngày tiếp theo (ngày thứ 8 sau 7 ngày trước)
        labels.append(df.iloc[i+1]["close_price"])

    return np.array(features), np.array(labels)

def train_model():
    try:
        print("Fetching data from API...")
        # Lấy dữ liệu từ API
        response = requests.get("http://localhost:8001/prices/resampling-day?days=0")
        if response.status_code == 200:
            data = response.json()["data"]

            # Tiền xử lý dữ liệu
            print("Preprocessing data...")
            X, y = preprocess_data(data)
            print(f"Features shape: {X.shape}, Labels shape: {y.shape}")

            # Chia dữ liệu thành train/test
            print("Splitting data into training and testing sets...")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Huấn luyện mô hình Random Forest
            print("Training model...")
            start_time = time.time()  # Thời gian bắt đầu huấn luyện
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            end_time = time.time()  # Thời gian kết thúc huấn luyện

            # In ra thời gian huấn luyện
            print(f"Training took {end_time - start_time:.2f} seconds")

            # Đánh giá mô hình
            score = model.score(X_test, y_test)
            print(f"Model R^2 score: {score:.2f}")

            # Lưu mô hình
            model_path = os.path.join(MODEL_DIR, "price_prediction_model.pkl")
            joblib.dump(model, model_path)
            # model_path = "/app/models/price_prediction_model.pkl"
            # joblib.dump(model, model_path)
            print(f"Model saved as '{model_path}'")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")
    
# if __name__ == "__main__":
#     train_model()  







