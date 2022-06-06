import { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import MonthlyPieChart from './MonthlyPieChars';
import CityStats from './CityStats';
import { CityPvInput } from '../types/PipepileInput';
import BuildingColorLegend from './BuildingColorLegend';

ChartJS.register(ArcElement, Tooltip, Legend);

function Dashboard () {
    const [pvData, setPvData] = useState<CityPvInput>();

    useEffect(() => {
        import('../../public/city-pv.json').then((loadedPvData: object)  => {
            setPvData(loadedPvData as CityPvInput);
           })
    }, []);

    return(
        <div className='right-container'>
            {
            !pvData  
            ? 
                "Loading dashboard..."
            : 
                <div>
                    <CityStats pvData={pvData}/>
                    <MonthlyPieChart pvData={pvData}/>
                    <BuildingColorLegend/>
                </div>
            }
        </div>
    );
}

export default Dashboard;