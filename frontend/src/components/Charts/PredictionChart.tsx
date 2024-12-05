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

const PredictionChart = () => {
  const [interval, setInterval] = useState(30);
  const [chartData, setChartData] = useState<any>(null);

  const { data: prediction } = useQuery({
    queryKey: ['prediction'],
    queryFn: async () => {
      const res = await axios.get('http://localhost:8001/get-prediction');
      return res.data;
    },
  });

  const { data } = useQuery({
    queryKey: ['time-data', interval],
    queryFn: async () => {
      const res = await axios.get(
        `http://localhost:8001/prices/resample?interval=day`,
      );
      return res?.data;
    },
    refetchInterval: 300000,
  });

  useEffect(() => {
    if (data) {
      const { periods, close_prices } = data.data;

      const lastPeriods = periods.slice(-interval);
      const lastClosePrices = close_prices.slice(-interval);

      const predictionTime = new Date(lastPeriods[lastPeriods.length - 1]);
      predictionTime.setDate(predictionTime.getDate() + 1);

      const predictionValue = prediction?.predict;

      const updatedPeriods = [
        ...lastPeriods,
        predictionTime.toISOString().split('T')[0],
      ];
      const updatedClosePrices = [...lastClosePrices, predictionValue];

      setChartData({
        labels: updatedPeriods,
        datasets: [
          {
            label: 'Price (USD)',
            data: lastClosePrices,
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 0,
          },
          {
            label: 'Predicted Price (USD)',
            data: Array(updatedClosePrices.length - 1)
              .fill(null)
              .concat([predictionValue]),
            borderColor: 'rgba(255, 99, 132, 1)',
            fill: false,
            pointBackgroundColor: 'rgba(255, 99, 132, 1)',
            pointRadius: 5,
            pointHoverRadius: 7,
            borderDash: [5, 5],
            pointHitRadius: 10,
          },
        ],
      });
    }
  }, [data, prediction]);

  if (!chartData?.labels?.length) {
    return <div>Loading...</div>;
  }

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  // Lấy ngày, tháng, năm
  const day = String(tomorrow.getDate()).padStart(2, '0'); // Đảm bảo luôn có 2 chữ số
  const month = String(tomorrow.getMonth() + 1).padStart(2, '0'); // Tháng cần +1 vì bắt đầu từ 0
  const year = tomorrow.getFullYear();

  // Ghép lại thành dd-mm-yyyy
  const formattedDate = `${day}-${month}-${year}`;

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-defaul sm:px-7.5 xl:col-span-6">
      <div className="flex justify-between items-center">
        <h2 className="text-black dark:text-white font-bold">
          DỰ ĐOÁN GIÁ CHO NGÀY MAI
        </h2>
        <div className="font-bold text-green-500">
          Dự đoán ngày {formattedDate}:{' '}
          <span className="text-red-500">{prediction?.predict} USD</span>
        </div>
        <div className="flex gap-3 items-center">
          <p className="text-black font-bold">Hiển thị theo: </p>
          <Select className="w-[100px]" onChange={setInterval} value={interval}>
            <Select.Option key={0}>Tất cả</Select.Option>
            <Select.Option key={7}>Tuần</Select.Option>
            <Select.Option key={30}>Tháng</Select.Option>
          </Select>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div className="h-125">
          <Line
            data={{
              labels: chartData.labels,
              datasets: chartData.datasets,
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
                    text: 'Date',
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: 'Price (USD)',
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

export default PredictionChart;
