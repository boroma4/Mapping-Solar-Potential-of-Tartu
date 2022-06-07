import React from "react";
import CitySelector from "../components/CitySelector";

interface Props {
    cities: string[];
    setCity: Function;
}

export default function MainPage({cities, setCity}: Props) {
  return (
    <div className={"center-content"} style={{backgroundColor: "#C2B280"}}>
        <h2> Welcome to the Project Solar X</h2>
        <h5>Pleace choose a city</h5>
        <CitySelector cities={cities} setCity={setCity} />
    </div>
  );
}

