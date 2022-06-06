import { Viewer, Cesium3DTileset, CesiumComponentRef } from "resium";
import { Viewer as CesiumViewer, Cesium3DTileset as Tileset, Cesium3DTileStyle, Ion } from "cesium";
import { useEffect, useRef } from "react";
import { yearlyPowerLegendKwh } from "../utils/YearlyPowerLegend";

Ion.defaultAccessToken=import.meta.env.VITE_CESIUM_ION_TOKEN;

function Map() {
    const ref = useRef<CesiumComponentRef<CesiumViewer>>(null);
    let viewer: CesiumViewer;
    
    useEffect(() => {
        if (ref.current?.cesiumElement) {
          viewer = ref.current.cesiumElement;
        }
    }, []);

    const createColorConditions = () => {
      const arr = Object.entries(yearlyPowerLegendKwh).sort((a, b) => Number(b[0])- Number(a[0]));
      return arr.map(([powerValueKwh, color]) => {
        return [`\${power} >= ${powerValueKwh}`, `color("${color}")`]
      });
    }

    const handleReady = async (tileset: Tileset)  => {
      const conditions = createColorConditions();
      tileset.style = new Cesium3DTileStyle({
          color : {
              conditions
          }
      });
      if (viewer) {
          await viewer.zoomTo(tileset);
          viewer.camera.zoomIn(5000);
      }
    };

  return (
    <Viewer ref={ref} timeline={false} animation={false} className="left-container">
      <Cesium3DTileset url={"/tileset.json"} 
        onReady={handleReady} 
        cullRequestsWhileMoving={false} 
        cullWithChildrenBounds={false}
        />
    </Viewer>
  );
}

export default Map;