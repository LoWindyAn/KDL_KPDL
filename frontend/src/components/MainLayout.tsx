import { Outlet } from "react-router-dom";
const MainLayout = () => {
  return (
    <div>
      <div>side bar</div>
      <div>
        Header
        <div className="bg-blue-500 text-white p-4">
          <h1 className="text-2xl">Hello, Tailwind CSS!</h1>
        </div>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
