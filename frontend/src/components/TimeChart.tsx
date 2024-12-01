import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2"; // Import Line chart from Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Đăng ký các thành phần của Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TimeChart = () => {
  const [interval, setInterval] = useState("week");
  const [chartData, setChartData] = useState<any>(null);

  const { data } = useQuery({
    queryKey: ["time-data", interval],
    queryFn: async () => {
      const res = await axios.get(
        `http://localhost:8001/prices/resample?interval=${interval}`
      );
      return res?.data;
    },
  });

  console.log("data:", data?.data);

  useEffect(() => {
    if (data) {
      const { periods, high_prices, low_prices, open_prices, close_prices } =
        data.data;

      setChartData({
        labels: periods,
        datasets: [
          {
            label: "High Price (USD)",
            data: high_prices,
            borderColor: "rgba(255, 99, 132, 1)",
            fill: false,
          },
          {
            label: "Low Price (USD)",
            data: low_prices,
            borderColor: "rgba(54, 162, 235, 1)",
            fill: false,
          },
          {
            label: "Open Price (USD)",
            data: open_prices,
            borderColor: "rgba(75, 192, 192, 1)",
            fill: false,
          },
          {
            label: "Closing Price (USD)",
            data: close_prices,
            borderColor: "rgba(153, 102, 255, 1)",
            fill: false,
          },
        ],
      });
    }
  }, [data]);

  // Kiểm tra nếu chưa có dữ liệu để render loading
  if (!chartData?.labels?.length) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Crypto Prices ({interval})</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* Biểu đồ High Price */}
        <div>
          {/* <h3>High Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels, // Các mốc thời gian
              datasets: [
                {
                  label: "High Price (USD)",
                  data: chartData.datasets[0].data, // Dữ liệu high_prices
                  borderColor: chartData.datasets[0].borderColor,
                  fill: false,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "High Price (USD) over Time",
                },
                tooltip: {
                  mode: "index",
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    text: "Date",
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: "Price (USD)",
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Low Price */}
        <div>
          {/* <h3>Low Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: "Low Price (USD)",
                  data: chartData.datasets[1].data, // Dữ liệu low_prices
                  borderColor: chartData.datasets[1].borderColor,
                  fill: false,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Low Price (USD) over Time",
                },
                tooltip: {
                  mode: "index",
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    text: "Date",
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: "Price (USD)",
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Open Price */}
        <div>
          {/* <h3>Open Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: "Open Price (USD)",
                  data: chartData.datasets[2].data, // Dữ liệu open_prices
                  borderColor: chartData.datasets[2].borderColor,
                  fill: false,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Open Price (USD) over Time",
                },
                tooltip: {
                  mode: "index",
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    text: "Date",
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: "Price (USD)",
                  },
                },
              },
            }}
          />
        </div>

        {/* Biểu đồ Closing Price */}
        <div>
          {/* <h3>Closing Price (USD)</h3> */}
          <Line
            data={{
              labels: chartData.labels,
              datasets: [
                {
                  label: "Closing Price (USD)",
                  data: chartData.datasets[3].data, // Dữ liệu close_prices
                  borderColor: chartData.datasets[3].borderColor,
                  fill: false,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  //   text: "Closing Price (USD) over Time",
                },
                tooltip: {
                  mode: "index",
                  intersect: false,
                },
              },
              scales: {
                x: {
                  title: {
                    display: true,
                    text: "Date",
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: "Price (USD)",
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

export default TimeChart;
