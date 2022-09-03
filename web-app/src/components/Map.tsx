import React from 'react';
import { Viewer, Cesium3DTileset, CesiumComponentRef } from 'resium';
import {
  Viewer as CesiumViewer, Cesium3DTileset as Tileset, Cesium3DTileStyle, Ion, Cartesian2, IntersectionTests, Ray
} from 'cesium';
import { useEffect, useRef, useState } from 'react';
import { yearlyPowerLegendKwh } from '../utils/YearlyPowerLegend';

Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_ION_TOKEN;

interface Props {
  city: string;
}

function Map({city}: Props) {
  const [isLoading, setIsLoading] = useState(true);
  const ref = useRef<CesiumComponentRef<CesiumViewer>>(null);
  let viewer: CesiumViewer;

  useEffect(() => {
    if (ref.current?.cesiumElement) {
      viewer = ref.current.cesiumElement;
    }
  }, []);

  const createColorConditions = () => {
    const arr = Object.entries(yearlyPowerLegendKwh).sort((a, b) => Number(b[0]) - Number(a[0]));
    return arr.map(([powerValueKwh, color]) => [`\${power} >= ${powerValueKwh}`, `color("${color}")`]);
  };

  const rotateMap = () => {
    const elmnt = document.getElementById("map");
    const ellipsoid = viewer.scene.mapProjection.ellipsoid;
    const windowCoordinates = new Cartesian2(elmnt!.offsetHeight / 2, elmnt!.offsetWidth / 2);
    const ray = viewer.camera.getPickRay(windowCoordinates);
    const intersection = IntersectionTests.rayEllipsoid(ray!, ellipsoid);
    const intersectionPoint = Ray.getPoint(ray!, intersection.start);
    viewer.camera.rotate(intersectionPoint, 0.7);
  }

  const handleReady = async (tileset: Tileset) => {
    const conditions = createColorConditions();
    tileset.style = new Cesium3DTileStyle({
      color: {
        conditions,
      },
    });
    if (viewer) {
      await viewer.zoomTo(tileset);
      viewer.camera.zoomIn(5000);
      
      // Rotate to prevent click unresponsiveness bug
      rotateMap();
    }
  };

  return (
    <div>
      {isLoading ? <div> Loading 3D buildings... </div> : <></>}
      <Viewer id={'map'} ref={ref} timeline={false} animation={false} className="left-container">
        <Cesium3DTileset
          url={`../../cities/${city}/tileset.json`}
          onReady={handleReady}
          onTileVisible={() => setIsLoading(false)}
          cullRequestsWhileMoving={false}
          cullWithChildrenBounds={false}
        />
      </Viewer>
    </div>
  );
}

export default Map;
