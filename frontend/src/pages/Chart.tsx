import React from 'react';

import CardDataStats from '../components/CardDataStats';
import TimeChart from '../components/Charts/TimeChart';
import TrendChart from '../components/Charts/TrendChart';
import CorrelationChart from '../components/Charts/CorrelationChart';
import SpiderChart from '../components/Charts/SpiderChart';
import PredictionChart from '../components/Charts/PredictionChart';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import RealTimeChart from '../components/Charts/RealTimeChart';

const Chart: React.FC = () => {
  const { data: prediction } = useQuery({
    queryKey: ['prediction'],
    queryFn: async () => {
      const res = await axios.get('http://localhost:8001/get-prediction');
      return res.data;
    },
  });

  const getTomorrowDate = () => {
    const today = new Date(); // Lấy ngày hôm nay
    today.setDate(today.getDate() + 1); // Thêm 1 ngày vào hôm nay để có ngày mai

    const day = today.getDate();
    const month = today.getMonth() + 1; // Tháng bắt đầu từ 0
    const year = today.getFullYear();

    // Định dạng "Ngày/Tháng/Năm"
    return `${day}/${month}/${year}`;
  };

  return (
    <>
      <div className=" gap-4 h-20 bg-white flex justify-center items-center">
        <p className="text-black-2 font-bold">
          BITCOIN PRICE ANALYSIS AND PREDICTION
        </p>
      </div>
      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
        <RealTimeChart />
      </div>
    </>
  );
};

export default Chart;
