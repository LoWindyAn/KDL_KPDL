import React, { useEffect, useState } from 'react';
//@ts-ignore
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Đăng ký các thành phần của Chart.js
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
);

const SpiderChart = () => {
  const [data, setData] = useState(null);

  // Giả sử bạn lấy dữ liệu từ API
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('http://localhost:8001/clusters');
      const result = await response.json();
      setData(result.clusters);
    };

    fetchData();
  }, []);

  // Kiểm tra nếu dữ liệu đã có
  if (!data) {
    return <div>Loading...</div>;
  }

  // Tạo dữ liệu cho biểu đồ Spider (Radar)
  const labels = ['High Price', 'Low Price', 'Open Price', 'Close Price'];

  // Màu sắc cho các clusters
  const colors = [
    'rgba(255, 99, 132, 0.2)', // Màu đỏ nhạt
    'rgba(54, 162, 235, 0.2)', // Màu xanh dương nhạt
    'rgba(255, 206, 86, 0.2)', // Màu vàng nhạt
    'rgba(75, 192, 192, 0.2)', // Màu xanh lá nhạt
    'rgba(153, 102, 255, 0.2)', // Màu tím nhạt
    'rgba(255, 159, 64, 0.2)', // Màu cam nhạt
  ];

  const borderColors = [
    'rgba(255, 99, 132, 1)', // Đường biên đỏ
    'rgba(54, 162, 235, 1)', // Đường biên xanh dương
    'rgba(255, 206, 86, 1)', // Đường biên vàng
    'rgba(75, 192, 192, 1)', // Đường biên xanh lá
    'rgba(153, 102, 255, 1)', // Đường biên tím
    'rgba(255, 159, 64, 1)', // Đường biên cam
  ];

  //@ts-ignore
  const clustersData = data.map((cluster, index) => ({
    label: `Cluster ${cluster.cluster_id}`,
    data: [
      cluster.high_price,
      cluster.low_price,
      cluster.open_price,
      cluster.close_price,
    ],
    backgroundColor: colors[index % colors.length], // Màu nền
    borderColor: borderColors[index % borderColors.length], // Màu đường biên
    borderWidth: 2, // Độ dày đường biên
    segment: {
      borderColor: [
        'rgba(255, 99, 132, 1)', // Đỏ
        'rgba(54, 162, 235, 1)', // Xanh dương
        'rgba(255, 206, 86, 1)', // Vàng
        'rgba(75, 192, 192, 1)', // Xanh lá
      ],
    },
  }));

  const chartData = {
    labels: labels,
    datasets: clustersData,
  };

  const chartOptions = {
    scale: {
      ticks: {
        beginAtZero: true,
      },
    },
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <div className="bg-white">
      <h2 className="flex justify-center m-3 text-black-2">
        Spider Chart for Clusters
      </h2>
      {/* @ts-ignore */}
      <Radar data={chartData} options={chartOptions} />
    </div>
  );
};

export default SpiderChart;
