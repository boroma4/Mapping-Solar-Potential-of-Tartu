import React from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
} from 'chart.js';
import { CityPvInput } from '../types/PipepileInput';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  pvData: CityPvInput
}

function MonthlyPieChart({ pvData }: Props) {
  const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const colors = ['#0000D1', '#000075', '#8AFF8A', '#00FF00', '#007500', '#FFFF00', '#FFA500', '#FF281B', '#6E612F', '#8A6E64', '#D1CEC5', '#5C5CFF'];

  const monthlyData = {
    labels,
    datasets: [{
      label: 'Monthly output',
      backgroundColor: colors,
      data: pvData.total_monthly_energy_kwh_list,
    }],
  };

  return (
    <div>
      <h4>Power produced by month (kWh): </h4>
      <Pie id="pie-char-1" data={monthlyData} />
    </div>
  );
}

export default MonthlyPieChart;
