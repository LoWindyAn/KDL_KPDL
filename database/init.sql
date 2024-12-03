CREATE DATABASE IF NOT EXISTS crypto_db;

USE crypto_db;

-- Tạo bảng crypto_prices
CREATE TABLE IF NOT EXISTS crypto_prices (
  time DATETIME PRIMARY KEY,              
  high_price DECIMAL(30, 10) NOT NULL,          
  low_price DECIMAL(30, 10) NOT NULL,          
  open_price DECIMAL(30, 10) NOT NULL,         
  close_price DECIMAL(30, 10) NOT NULL,               
  volume_btc DECIMAL(30, 10) NOT NULL,         
  volume_usd DECIMAL(30, 10) NOT NULL            
);

-- Tạo bảng clusters
CREATE TABLE IF NOT EXISTS clusters (
    cluster_id INT PRIMARY KEY,     
    high_price FLOAT NOT NULL,              
    low_price FLOAT NOT NULL,               
    open_price FLOAT NOT NULL,             
    close_price FLOAT NOT NULL             
);
