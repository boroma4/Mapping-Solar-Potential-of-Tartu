import { CityPvInput } from "../types/PipepileInput";
import { adjustPowerUnits } from "../utils/AdjustUnits";

interface Props {
    pvData: CityPvInput
}

function CityStats ({ pvData }: Props) {
    const adjustYearlyEnergy = () => {
        const adjusted = adjustPowerUnits(pvData.total_yearly_energy_kwh);
        return `${adjusted.value.toFixed(4)} ${adjusted.units}`
    }

    return(
        <div>
            <h4>From file: </h4> 
            <p>{pvData.file}</p>
            <h4>Total yearly power output: </h4>
            <p>
            { adjustYearlyEnergy() } 
            </p>
        </div>
    );
}

export default CityStats;