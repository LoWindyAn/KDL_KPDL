import CorrelationChart from '../components/Charts/CorrelationChart';
import SpiderChart from '../components/Charts/SpiderChart';
import TrendChart from '../components/Charts/TrendChart';

const Profile: React.FC = () => {
  return (
    <>
      <div className=" grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
        <div className="col-span-12 rounded-sm border gap-4 flex flex-col  shadow-defaul  xl:col-span-6">
          {/* <CorrelationChart /> */}
          <TrendChart title="trend" subTitle="Trend của dữ liệu" />
          <TrendChart title="seasonal" subTitle="Seasonal line" />
        </div>
        <div className="col-span-12 rounded-sm  border gap-4 flex flex-col  shadow-defaul  xl:col-span-6">
          <SpiderChart />
        </div>
      </div>
    </>
  );
};

export default Profile;
