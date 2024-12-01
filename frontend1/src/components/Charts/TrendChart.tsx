import { useQuery } from '@tanstack/react-query';
import { Select } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const TrendChart = ({ title, subTitle }: any) => {
  const [interval, setInterval] = useState('day');
  const [chartData, setChartData] = useState<any>(null);

  const { data } = useQuery({
    queryKey: ['trend-data', interval],
    queryFn: async () => {
      const res = await axios.get(
        `http://localhost:8001/prices/trend?interval=${interval}`,
      );
      return res?.data?.data;
    },
    refetchInterval: 300000,
  });

  useEffect(() => {
    if (data) {
      setChartData({
        labels: data?.periods, // Mốc thời gian (periods)
        datasets: [
          {
            label: 'Price Trend',
            data: data?.[`${title}`], // Dữ liệu xu hướng (trend)
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: false,
          },
        ],
      });
    }
  }, [data]);

  console.log(chartData);

  if (!chartData) {
    return <div>Loading...</div>;
  }

  return (
    <div className="bg-white p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-black dark:text-white font-bold">
          {subTitle} ({interval})
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
        {/* Biểu đồ High Price */}
        <div>
          <Line
            data={{
              labels: chartData.labels, // Các mốc thời gian
              datasets: [
                {
                  label: '',
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
      </div>
    </div>
  );
};

export default TrendChart;
