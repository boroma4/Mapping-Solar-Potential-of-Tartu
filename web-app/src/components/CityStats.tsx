import { CityPvInput } from "../types/PipepileInput";

interface Props {
    pvData: CityPvInput
}

function CityStats ({ pvData }: Props) {
    return(
        <div>
            <h4>City name: </h4> 
            <p>{pvData.city}</p>
            <h4>Total yearly power output: </h4>
            <p>
            {pvData.total_yearly_energy_kwh} kWh
            </p>
        </div>
    );
}

export default CityStats;