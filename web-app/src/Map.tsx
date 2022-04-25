import { Viewer, Cesium3DTileset, CesiumComponentRef } from "resium";
import { Viewer as CesiumViewer, Cesium3DTileset as Tileset, Cesium3DTileStyle} from "cesium";
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
    // tileset.style = new Cesium3DTileStyle({
    //     color : {
    //         conditions : [
    //             ['${area} >= 100', 'color("purple", 0.5)'],
    //             ['${area} >= 50', 'color("red")'],
    //             ['true', 'color("blue")']
    //         ]
    //     },
    //     meta : {
    //         description : '"Building id ${id} has height."'
    //     }
    //  });
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