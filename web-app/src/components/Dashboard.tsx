import React from 'react';
import { useEffect, useState } from 'react';
import {
  Chart as ChartJS, ArcElement, Tooltip, Legend,
} from 'chart.js';
import MonthlyPieChart from './MonthlyPieChars';
import CityStats from './CityStats';
import { CityPvInput } from '../types/PipepileInput';
import BuildingColorLegend from './BuildingColorLegend';
import BuildingDescriptionLegend from './BuildingDescriptionLegend';

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  city: string;
}

function Dashboard({city}: Props) {
  const [pvData, setPvData] = useState<CityPvInput>();

  useEffect(() => {
    import(`../../cities/${city}/city-pv.json`).then((loadedPvData: object) => {
      setPvData(loadedPvData as CityPvInput);
    });
  }, []);

  return (
    <div className="right-container">
      {
            !pvData
              ? 'Loading dashboard...'
              : (
                <div style={{overflowY: "scroll", height: "100vh"}}>
                  <CityStats pvData={pvData} />
                  <MonthlyPieChart pvData={pvData} />
                  <BuildingColorLegend />
                  <BuildingDescriptionLegend/>
                </div>
              )
      }
    </div>
  );
}

export default Dashboard;
