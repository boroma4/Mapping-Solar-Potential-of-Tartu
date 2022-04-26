import Dashboard from "./components/Dashboard";
import Map from "./components/Map";
import "./App.css";

function App() {
  return (
    <div className="main-container">
      <Map/>
      <Dashboard/>
    </div>
  );
}

export default App;