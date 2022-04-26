import { useEffect, useState } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import MonthlyPieChart from './MonthlyPieChars';
import CityStats from './CityStats';
import { CityPvInput } from '../types/PipepileInput';

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
                "loading" 
            : 
                <>
                    <CityStats pvData={pvData}/>
                    <MonthlyPieChart pvData={pvData}/>
                </>
            }
        </div>
    );
}

export default Dashboard;