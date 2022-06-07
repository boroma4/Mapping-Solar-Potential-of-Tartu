import React from "react";
import Select from 'react-select'
import { capitalizeFirstLetter } from "../utils/CapitalizeFirstLetter";


interface Props {
    cities: string[]
    setCity: Function
}

const CitySelector = ({cities, setCity}: Props) => {
    const makeOptions = () => {
        return cities.map((city) => {
            return {value: city, label: capitalizeFirstLetter(city)};
        })
    }

    return(
        <Select options={makeOptions()} onChange={(newValue) => setCity(newValue?.value)}/>
    )

}


export default CitySelector;