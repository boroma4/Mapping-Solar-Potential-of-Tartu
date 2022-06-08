import React from "react";
import Dashboard from "../components/Dashboard";
import Map from "../components/Map";

interface Props {
    city: string
}

export default function MapPage({city}: Props) {
  return (
    <div className="flex-container">
        <Map city={city}/>
        <Dashboard city={city}/>
    </div>
  );
}

