import React from 'react';

export default function BuildingDescriptionLegend() {
  return (
    <>
      <h4>Building description legend:</h4>
      <table>
        <tr>
            <th>area</th>
            <td>Total roof area</td>
        </tr>
        <tr>
            <th>north-area</th>
            <td>Area of roof surfaces facing North</td>
        </tr>
        <tr>
            <th>south-area</th>
            <td>Area of roof surfaces facing South</td>
        </tr>
        <tr>
            <th>west-area</th>
            <td>Area of roof surfaces facing West</td>
        </tr>
        <tr>
            <th>east-area</th>
            <td>Area of roof surfaces facing East</td>
        </tr>
        <tr>
            <th>flat-area</th>
            <td>Area of roof surfaces with tilt less that 10°</td>
        </tr>
        <tr>
            <th>power</th>
            <td>Estimated total solar power</td>
        </tr>
        <tr>
            <th>north-power</th>
            <td>Estimated solar power produced from roof surfaces facing North</td>
        </tr>
        <tr>
            <th>south-power</th>
            <td>Estimated solar power produced from roof surfaces facing South</td>
        </tr>
        <tr>
            <th>west-power</th>
            <td>Estimated solar power produced from roof surfaces facing West</td>
        </tr>
        <tr>
            <th>East-power</th>
            <td>Estimated solar power produced from roof surfaces facing East</td>
        </tr>
        <tr>
            <th>optimized-power</th>
            <td>Estimated solar power produced from flat roof surfaces with optimal angles of solar panels</td>
        </tr>
      </table>
      <div style={{height: "10px"}}/>
    </>
  );
}