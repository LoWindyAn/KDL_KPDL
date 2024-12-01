import "./App.css";
import MainLayout from "./components/MainLayout";
import TimeChart from "./components/TimeChart";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="/time-chart" element={<TimeChart />} />
          <Route path="/about" element={"abc"} />
          <Route path="*" element={"abc"} />{" "}
          {/* Catch-all for unknown routes */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
