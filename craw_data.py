import requests
import time
import pandas as pd

# Thời gian bắt đầu (3 năm trước từ hiện tại)
end_time = int(time.time())  # Timestamps hiện tại
start_time = end_time - (8 * 365 * 24 * 60 * 60)  # 3 năm trước

# API endpoint và các tham số
url = "https://min-api.cryptocompare.com/data/v2/histohour"
fsym = "BTC"
tsym = "USD"
limit = 2000  # Giới hạn tối đa mỗi lần gọi API

# Hàm để lấy dữ liệu từng phần (chunk) 2000 giờ
def get_data_chunk(start_ts, end_ts):
    params = {
        'fsym': fsym,
        'tsym': tsym,
        'limit': limit,
        'toTs': end_ts,  # Thời gian kết thúc (timestamp)
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['Data']['Data']

# Lấy dữ liệu trong nhiều yêu cầu
all_data = []
while end_time > start_time:
    data_chunk = get_data_chunk(start_time, end_time)
    all_data.extend(data_chunk)
    # Cập nhật lại thời gian bắt đầu cho lần gọi tiếp theo (dùng time từ cuối dữ liệu vừa lấy)
    end_time = data_chunk[0]['time'] - 1  # Cập nhật thời gian kết thúc mới (trước 1 giây của dữ liệu đầu tiên)
    print(f"Fetched {len(data_chunk)} data points, New end_time: {end_time}")

# Chuyển dữ liệu thành DataFrame của pandas
df = pd.DataFrame(all_data)

# Chuyển đổi timestamp thành datetime
df['time'] = pd.to_datetime(df['time'], unit='s')

# Đưa thời gian về múi giờ UTC (nếu chưa có múi giờ)
df['time'] = df['time'].dt.tz_localize('UTC')

# Chuyển thời gian sang múi giờ Việt Nam (Asia/Ho_Chi_Minh)
df['time'] = df['time'].dt.tz_convert('Asia/Ho_Chi_Minh')

# Loại bỏ thông tin múi giờ khỏi datetime
df['time'] = df['time'].dt.tz_localize(None)

# Đặt lại tên cột cho dễ hiểu
df.rename(columns={
    'time': 'time',
    'open':'open_price',
    'close': 'close_price',
    'high':'high_price',
    'low':'low_price',
    'volumefrom': 'volume_btc',
    'volumeto': 'volume_usd',
}, inplace=True)

# Chỉ chọn các cột cần thiết
df = df[['time', 'high_price','low_price', 'open_price', 'close_price','volume_btc','volume_usd']]

# Xuất ra file CSV
output_file = 'bitcoin_data_8_years.csv'
df.to_csv(output_file, index=False)

print(f"Data exported to {output_file}")