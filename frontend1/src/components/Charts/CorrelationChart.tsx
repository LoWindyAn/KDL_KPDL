import Plot from 'react-plotly.js';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const CorrelationChart = () => {
  const { data: correlationMatrix } = useQuery({
    queryKey: ['correlation-data'],
    queryFn: async () => {
      const res = await axios.get('http://localhost:8001/prices/correlation');
      return res.data?.correlation_matrix;
    },
    refetchInterval: 300000,
  });

  if (!correlationMatrix) {
    return <div>Loading...</div>;
  }

  // Chuyển đổi ma trận tương quan thành dữ liệu cho Plotly
  const labels = Object.keys(correlationMatrix);
  const matrixData = labels.map((row) =>
    labels.map((col) => correlationMatrix[row][col]),
  );

  // Tạo textMatrix: ma trận 2 chiều giống với matrixData
  const textMatrix = matrixData.map(
    (row) => row.map((value) => value.toFixed(2)), // Làm tròn và chuyển thành chuỗi
  );

  return (
    <div>
      <Plot
        data={[
          {
            x: labels,
            y: labels,
            z: matrixData,
            type: 'heatmap',
            colorscale: 'YlOrRd',
            // @ts-ignore: Bỏ qua kiểm tra kiểu TypeScript cho text
            text: textMatrix, // Truyền mảng 1 chiều
            texttemplate: '%{text}', // Sử dụng text
            textfont: {
              size: 10, // Kích thước chữ
              color: 'black', // Màu chữ
            },
          },
        ]}
        layout={{
          title: 'Correlation Matrix',
          xaxis: {
            automargin: true,
          },
          yaxis: {
            automargin: true,
          },
        }}
      />
    </div>
  );
};

export default CorrelationChart;
