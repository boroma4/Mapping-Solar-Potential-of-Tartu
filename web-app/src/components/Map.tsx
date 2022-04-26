import { Viewer, Cesium3DTileset, CesiumComponentRef, Camera } from "resium";
import { Viewer as CesiumViewer, Cesium3DTileset as Tileset, Cesium3DTileStyle, Cartesian3} from "cesium";
import { useEffect, useRef } from "react";
import { yearlyPowerLegendKwh } from "../utils/YearlyPowerLegend";

function Map() {
    const ref = useRef<CesiumComponentRef<CesiumViewer>>(null);
    let viewer: CesiumViewer;
    
    useEffect(() => {
        if (ref.current?.cesiumElement) {
          viewer = ref.current.cesiumElement;
        }
    }, []);



    const createColorConditions = () => {
      const arr = Object.entries(yearlyPowerLegendKwh).sort((a, b) => Number(b[0])- Number(a[0]))
      return arr.map(([powerValueKwh, color]) => {
        return [`\${power} >= ${powerValueKwh}`, `color("${color}")`]
      });
    }

  

    const handleReady = (tileset: Tileset)  => {
      const conditions = createColorConditions();
      tileset.style = new Cesium3DTileStyle({
          color : {
              conditions
          },
          meta : {
              description : '"Building id ${id} has height."'
          }
      });
      if (viewer) {
          viewer.zoomTo(tileset);
      }
    };

  return (
    <Viewer ref={ref} timeline={false} animation={false} className="left-container">
      <Cesium3DTileset url={"/tileset.json"} onReady={handleReady} />
    </Viewer>
  );
}

export default Map;