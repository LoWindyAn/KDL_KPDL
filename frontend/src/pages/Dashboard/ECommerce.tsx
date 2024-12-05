import React from 'react';
import PredictionChart from '../../components/Charts/PredictionChart';

const ECommerce: React.FC = () => {
  return (
    <>
      <div className=" gap-4 h-20 bg-white flex justify-center items-center">
        <p className="text-black-2 font-bold">
          BITCOIN PRICE ANALYSIS AND PREDICTION
        </p>
      </div>
      <div className="mt-10">
        <PredictionChart />
      </div>
    </>
  );
};

export default ECommerce;
