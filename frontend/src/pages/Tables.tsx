import CorrelationChart from '../components/Charts/CorrelationChart';

const Tables = () => {
  return (
    <>
      <div className=" gap-4 h-20 bg-white flex justify-center items-center">
        <p className="text-black-2 font-bold">
          BITCOIN PRICE ANALYSIS AND PREDICTION
        </p>
      </div>
      <div className="mt-10">
        <CorrelationChart />
      </div>
    </>
  );
};

export default Tables;
