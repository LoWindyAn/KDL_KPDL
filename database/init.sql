CREATE DATABASE IF NOT EXISTS crypto_db;

USE crypto_db;

CREATE TABLE IF NOT EXISTS crypto_prices (
  time DATETIME PRIMARY KEY,              
  high_price DECIMAL(30, 10) NOT NULL,          
  low_price DECIMAL(30, 10) NOT NULL,          
  open_price DECIMAL(30, 10) NOT NULL,         
  close_price DECIMAL(30, 10) NOT NULL,               
  volume_btc DECIMAL(30, 10) NOT NULL,         
  volume_usd DECIMAL(30, 10) NOT NULL            
);

CREATE TABLE IF NOT EXISTS clusters (
    cluster_id INT PRIMARY KEY,     
    high_price FLOAT NOT NULL,              
    low_price FLOAT NOT NULL,               
    open_price FLOAT NOT NULL,             
    close_price FLOAT NOT NULL             
);

CREATE TABLE IF NOT EXISTS prediction (
    time DATETIME PRIMARY KEY, 
    predict FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS correlation_matrix (
    metric1 VARCHAR(50),
    metric2 VARCHAR(50),
    correlation FLOAT,
    PRIMARY KEY (metric1, metric2)
)
