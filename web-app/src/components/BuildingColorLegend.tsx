import React from 'react';
import { yearlyPowerLegendKwh } from '../utils/YearlyPowerLegend';

export default function BuildingColorLegend() {
  return (
    <>
      <h4>Building color legend:</h4>
      <Legend />
    </>
  );
}

function ColoredLine({ color } : {color: string}) {
  return (
    <hr
      style={{
        color,
        backgroundColor: color,
        height: 5,
      }}
    />
  );
}

function Legend() {
  return (
    <>
      {
          Object.entries(yearlyPowerLegendKwh).map(([powerKwh, color]) => (
            <div key={color}>
              {`>= ${powerKwh} kWh`}
              <ColoredLine color={color} />
            </div>
          ))
        }
    </>
  );
}
