import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2'; // Import Line chart from Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Select } from 'antd';

// Đăng ký các thành phần của Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

const TimeChart = () => {
  const [interval, setInterval] = useState('day');
  const [chartData, setChartData] = useState<any>(null);

  const { data } = useQuery({
    queryKey: ['time-data', interval],
    queryFn: async () => {
      const res = await axios.get(
        `http://localhost:8001/prices/resample?interval=${interval}`,
      );
      return res?.data;
    },
    refetchInterval: 300000,
  });

  useEffect(() => {
    if (data) {
      const {
        periods,
        high_prices,
        low_prices,
        open_prices,
        close_prices,
        volume_btc,
        volume_usd,
      } = data.data;

      setChartData({
        labels: periods,
        datasets: [
          {
            // label: 'High Price (USD)',
            data: high_prices,
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: false,
          },
          {
            label: 'Low Price (USD)',
            data: low_prices,
            borderColor: 'rgba(54, 162, 235, 1)',
            fill: false,
          },
          {
            label: 'Open Price (USD)',
            data: open_prices,
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false,
          },
          {
            label: 'Closing Price (USD)',
            data: close_prices,
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
          },
          {
            label: 'Volume BTC',
            data: volume_btc,
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
          },
          {
            label: 'Volume USD',
            data: volume_usd,
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
          },
        ],
      });
    }
  }, [data]);

  // Kiểm tra nếu chưa có dữ liệu để render loading
  if (!chartData?.labels?.length) {
    return <div>Loading...</div>;
  }

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-defaul sm:px-7.5 xl:col-span-6">
      <div className="flex justify-between items-center">
        <h2 className="text-black dark:text-white font-bold">
          Dữ liệu theo thời gian ({interval})
        </h2>
        <Select
          className="w-[100px]"
          defaultValue={'day'}
          onChange={setInterval}
        >
          {/* <Select.Option key={'hour'}>Giờ</Select.Option> */}
          <Select.Option key={'day'}>Ngày</Select.Option>
          <Select.Option key={'week'}>Tuần</Select.Option>
          <Select.Option key={'month'}>Tháng</Select.Option>
        </Select>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {/* Biểu đồ High Price */}
        <div>
          <Line
            data={{
              labels: chartData.labels, // Các mốc thời gian
              datasets: [
                {
                  label: 'High Price (USD)',
                  data: chartData.datasets[0].data, // Dữ liệu high_prices
                  borderColor: chartData.datasets[0].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            // height={150}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "High Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Low Price */}
        <div>
          {/* <h3>Low Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Low Price (USD)',
                  data: chartData.datasets[1].data, // Dữ liệu low_prices
                  borderColor: chartData.datasets[1].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Low Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Open Price */}
        <div>
          {/* <h3>Open Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Open Price (USD)',
                  data: chartData.datasets[2].data, // Dữ liệu open_prices
                  borderColor: chartData.datasets[2].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Open Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Closing Price */}
        <div>
          {/* <h3>Closing Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Closing Price (USD)',
                  data: chartData.datasets[3].data, // Dữ liệu close_prices
                  borderColor: chartData.datasets[3].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Closing Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>
        <div>
          {/* <h3>Closing Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Volume BTC',
                  data: chartData.datasets[4].data, // Dữ liệu close_prices
                  borderColor: chartData.datasets[4].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Closing Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>
        <div>
          {/* <h3>Closing Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Volume USD',
                  data: chartData.datasets[5].data, // Dữ liệu close_prices
                  borderColor: chartData.datasets[5].borderColor,
                  fill: false,
                  pointRadius: 0, // Ẩn các điểm tròn
                  pointHoverRadius: 0, // Ẩn điểm khi hover
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Closing Price (USD) over Time",
                },
                tooltip: {
                  mode: 'index',
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    // text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    // text: 'Price (USD)',
                  },
                },
              },
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default TimeChart;
