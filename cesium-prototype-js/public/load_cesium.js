Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIzMmNhMmE2NC1kMWMwLTQyMDMtYTJkNS04Y2MwZmU5ODJiMTciLCJpZCI6NzI2MjMsImlhdCI6MTYzNjIwMjExOX0.PnQgGga-vVnFyiWAoWVY1_ZO_mYSkIyylnq1L6XBXMM';

var viewer = new Cesium.Viewer('cesiumContainer');
var tileset = viewer.scene.primitives.add(new Cesium.Cesium3DTileset({
     url: "../model/tileset.json",
}))
Cesium.when(tileset.readyPromise).then(function (tileset) {
    viewer.flyTo(tileset);
    colorByArea();
})

// chroma.scale(['#fafa6e','#2A4858']).mode('lch').colors(6)
function colorByArea () {
    tileset.style = new Cesium.Cesium3DTileStyle({
        color: {
            conditions: [
                ['${area} >= 5000', 'color("#FF442E", 0.5)'],
                ['${area} >= 3000', 'color("#FF8000", 0.5)'],
                ['${area} >= 1000', 'color("#E7A700", 0.5)'],
                ['${area} >= 500', 'color("#CFC600", 0.5)'],
                ['${area} >= 100', 'color("#A4B600", 0.5)'],
                ['${area} >= 0', 'color("#6A9E00", 0.5)'],
                ['true', 'rgb(127, 59, 8)']
            ]
        }
    });
}

