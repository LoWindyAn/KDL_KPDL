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
