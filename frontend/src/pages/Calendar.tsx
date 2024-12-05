import TimeChart1 from '../components/Charts/TimeChart1';

const Calendar = () => {
  return (
    <>
      <div className=" gap-4 h-20 bg-white flex justify-center items-center">
        <p className="text-black-2 font-bold text-2xl">
          BITCOIN PRICE ANALYSIS AND PREDICTION
        </p>
      </div>

      <div className="mt-4 grid grid-cols-12 gap-4">
        <TimeChart1 />
      </div>
    </>
  );
};

export default Calendar;
