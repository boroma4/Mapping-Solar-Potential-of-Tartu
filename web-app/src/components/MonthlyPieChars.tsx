import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { CityPvInput } from '../types/PipepileInput';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  pvData: CityPvInput
}

function MonthlyPieChart ({ pvData }: Props) {
    const labels = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const colors = [ "#b30000", "#7c1158", "#4421af", "#808000", "#0d88e6", "#00b7c7", "#D73B3E", "#8be04e", "#ebdc78","#FF9966","#D2691E", "#FFC0CB"];

    const monthlyData =  {
            labels: labels,
            datasets: [{
              label: 'Monthly output',
              backgroundColor: colors,
              data: pvData.total_monthly_energy_kwh_list,
            }]
    };

    return(
        <Pie id='pie-char-1' data={monthlyData}/>
    );
}

export default MonthlyPieChart;