import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Tải mô hình đã lưu

class PricePredictionRequest(BaseModel):
    # Mỗi đối tượng yêu cầu dữ liệu của 7 ngày trước đó với các giá mở cửa, cao nhất, thấp nhất và đóng cửa.
    open_price: list[float]
    high_price: list[float]
    low_price: list[float]
    close_price: list[float]

def preprocess_input(data: PricePredictionRequest):
    # Chuyển đổi dữ liệu đầu vào thành dạng đặc trưng (features) cho mô hình
    features = np.array([
        data.open_price + data.high_price + data.low_price + data.close_price
    ])
    return features

@app.post("/predict/")
def predict(data: PricePredictionRequest):

    model = joblib.load("models/price_prediction_model.pkl")

    try:
        # Tiền xử lý dữ liệu đầu vào
        features = preprocess_input(data)
        
        # Dự đoán với mô hình đã tải
        prediction = model.predict(features)
        
        # Trả về dự đoán
        return {"predicted_close_price": prediction[0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
