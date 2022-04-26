import { adjustPowerUnits } from "../utils/AdjustUnits";
import { yearlyPowerLegendKwh } from "../utils/YearlyPowerLegend";



function BuildingColorLegend () {
    const ColoredLine = ({ color } : {color: string}) => (
        <hr
            style={{
                color: color,
                backgroundColor: color,
                height: 5
            }}
        />
    );

    const Legend = () => {
        return(
        <>
            {
                Object.entries(yearlyPowerLegendKwh).map(([powerKwh, color]) => {
                return(
                    <>
                        {`>= ${powerKwh} kWh`}
                        <ColoredLine color={color}/>
                    </>
                )
            })
            }
        </>);
    };

    return(
        <>
            <h4>Building color legend:</h4>
            <Legend />
        </>
    );
}

export default BuildingColorLegend;