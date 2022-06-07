import React from "react";
import Select from 'react-select'


interface Props {
    cities: string[]
    setCity: Function
}

const CitySelector = ({cities, setCity}: Props) => {
    const makeOptions = () => {
        return cities.map((city) => {
            return {value: city, label: city};
        })
    }

    return(
        <Select options={makeOptions()} onChange={(newValue) => setCity(newValue?.value)}/>
    )

}


export default CitySelector;