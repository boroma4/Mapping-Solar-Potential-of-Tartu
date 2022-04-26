import { Viewer, Cesium3DTileset, CesiumComponentRef, Camera } from "resium";
import { Viewer as CesiumViewer, Cesium3DTileset as Tileset, Cesium3DTileStyle, Cartesian3} from "cesium";
import { useEffect, useRef } from "react";

function Map() {
    const ref = useRef<CesiumComponentRef<CesiumViewer>>(null);
    let viewer: CesiumViewer;
    
    useEffect(() => {
        if (ref.current?.cesiumElement) {
          viewer = ref.current.cesiumElement;
        }
      }, []);

  const handleReady = (tileset: Tileset)  => {
    tileset.style = new Cesium3DTileStyle({
        color : {
            conditions : [
                ['${power} >= 50000', 'color("red")'],
                ['${power} >= 20000', 'color("orange")'],                
                ['${power} >= 10000', 'color("yellow")'],
                ['${power} >= 5000', 'color("green")'],
                ['true', 'color("grey")']
            ]
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