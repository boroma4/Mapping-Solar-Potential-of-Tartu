import React, { useState } from "react";
import "./App.css";
import cities from "../cities/meta.json";
import MapPage from "./pages/MapPage";
import MainPage from "./pages/MainPage";

function App() {
  const [city, setCity] = useState("");
  return (
    <>
      {
        city 
        ?
          <MapPage city={city} />
        : 
          <MainPage cities={cities.list} setCity={setCity} />
        }
    </>
  );
}

export default App;