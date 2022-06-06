export interface AdjustedPower {
    value: number;
    units: string;
}

export const adjustPowerUnits = (energyValue: number): AdjustedPower => {
  const thousand = 10 ** 3;
  const million = 10 ** 6;
  let output: AdjustedPower = { value: energyValue, units: 'kWh' };

  if (energyValue > million) {
    output = { value: energyValue / million, units: 'GWh' };
  } else if (energyValue > thousand) {
    output = { value: energyValue / thousand, units: 'MWh' };
  }

  return output;
};
