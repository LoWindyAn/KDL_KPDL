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
import { Card, Select, Skeleton } from 'antd';

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

const TimeChart1 = () => {
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
    return <Card style={{ width: '1200px' }} className="w-full" loading />;
  }

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-defaul sm:px-7.5 xl:col-span-12">
      <div className="flex justify-between items-center">
        <h2 className="text-black dark:text-white font-bold text-xl">
          DỮ LIỆU THEO THỜI GIAN
        </h2>
        <Select
          className="w-[100px]"
          defaultValue={'day'}
          onChange={setInterval}
        >
          <Select.Option key={'day'}>Ngày</Select.Option>
          <Select.Option key={'week'}>Tuần</Select.Option>
          <Select.Option key={'month'}>Tháng</Select.Option>
        </Select>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'High Price (USD)',
                  data: chartData.datasets[0].data,
                  borderColor: chartData.datasets[0].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
                  },
                },
              },
            }}
          />
        </div>

        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Low Price (USD)',
                  data: chartData.datasets[1].data,
                  borderColor: chartData.datasets[1].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
                  },
                },
              },
            }}
          />
        </div>

        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Open Price (USD)',
                  data: chartData.datasets[2].data,
                  borderColor: chartData.datasets[2].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
                  },
                },
              },
            }}
          />
        </div>

        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Closing Price (USD)',
                  data: chartData.datasets[3].data,
                  borderColor: chartData.datasets[3].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
                  },
                },
              },
            }}
          />
        </div>
        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Volume BTC',
                  data: chartData.datasets[4].data,
                  borderColor: chartData.datasets[4].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
                  },
                },
              },
            }}
          />
        </div>
        <div style={{ height: '250px', width: '100%' }}>
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: 'Volume USD',
                  data: chartData.datasets[5].data,
                  borderColor: chartData.datasets[5].borderColor,
                  fill: false,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ],
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
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
                  },
                },
                y: {
                  title: {
                    display: true,
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

export default TimeChart1;
