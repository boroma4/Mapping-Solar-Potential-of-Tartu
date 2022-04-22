import { Viewer, Cesium3DTileset } from "resium";

function App() {
  let viewer: Viewer; // This will be raw Cesium's Viewer object.

  const handleReady = tileset => {
    if (viewer) {
      viewer.zoomTo(tileset);
    }
  };

  return (
    <Viewer
      full
      ref={e => {
        viewer = e && e.cesiumElement;
      }}>
      <Cesium3DTileset url={"/tileset.json"} onReady={handleReady} />
    </Viewer>
  );
}

export default App;