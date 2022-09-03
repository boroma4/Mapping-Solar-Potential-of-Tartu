import React from 'react';

export default function BuildingDescriptionLegend() {
  return (
    <>
      <h4>Building description legend:</h4>
      <table>
        <tr>
            <th>etak_id</th>
            <td>ID of the building in the <a href='https://geoportaal.maaamet.ee/est/Ruumiandmed/Eesti-topograafia-andmekogu-p79.html'>ETAK</a> registry</td>
        </tr>
        <tr>
            <th>area</th>
            <td>Total roof area <b>(m2)</b></td>
        </tr>
        <tr>
            <th>north-area</th>
            <td>Area of roof surfaces facing North <b>(m2)</b></td>
        </tr>
        <tr>
            <th>south-area</th>
            <td>Area of roof surfaces facing South <b>(m2)</b></td>
        </tr>
        <tr>
            <th>west-area</th>
            <td>Area of roof surfaces facing West <b>(m2)</b></td>
        </tr>
        <tr>
            <th>east-area</th>
            <td>Area of roof surfaces facing East <b>(m2)</b></td>
        </tr>
        <tr>
            <th>flat-area</th>
            <td>Area of roof surfaces with tilt less that 10° <b>(m2)</b></td>
        </tr>
        <tr>
            <th>power</th>
            <td>Estimated total solar power <b>(kWh)</b></td>
        </tr>
        <tr>
            <th>north-power</th>
            <td>Estimated solar power produced from roof surfaces facing North <b>(kWh)</b></td>
        </tr>
        <tr>
            <th>south-power</th>
            <td>Estimated solar power produced from roof surfaces facing South <b>(kWh)</b></td>
        </tr>
        <tr>
            <th>west-power</th>
            <td>Estimated solar power produced from roof surfaces facing West <b>(kWh)</b></td>
        </tr>
        <tr>
            <th>east-power</th>
            <td>Estimated solar power produced from roof surfaces facing East <b>(kWh)</b></td>
        </tr>
        <tr>
            <th>optimized-power</th>
            <td>Estimated solar power produced from flat roof surfaces with optimal angles of solar panels <b>(kWh)</b></td>
        </tr>
      </table>
      <div style={{height: "10px"}}/>
    </>
  );
}