import React from 'react';
import TimeChart from '../../components/Charts/TimeChart';
import CorrelationChart from '../../components/Charts/CorrelationChart';
import TrendChart from '../../components/Charts/TrendChart';
import SpiderChart from '../../components/Charts/SpiderChart';
import PredictionChart from '../../components/Charts/PredictionChart';

const ECommerce: React.FC = () => {
  return (
    <>
      <div className=" gap-4 h-20 bg-white flex justify-center items-center">
        <p className="text-black-2 font-bold">
          Bitcoin Price Analysis and Prediction
        </p>
      </div>

      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
        <TimeChart />
        <div className="col-span-12 rounded-sm border gap-4 flex flex-col  shadow-defaul  xl:col-span-6">
          <TrendChart title="trend" subTitle="Trend của dữ liệu" />
          <TrendChart title="seasonal" subTitle="Seasonal line" />
          <CorrelationChart />
          <SpiderChart />
        </div>
        <div></div>
      </div>
      <PredictionChart />
    </>
  );
};

export default ECommerce;
