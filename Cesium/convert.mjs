import Converter from "citygml-to-3dtiles";

let converter = new Converter({
    srsProjections: {
      'EPSG:3301': '+proj=lcc +lat_1=59.33333333333334 +lat_2=58 +lat_0=57.51755393055556 +lon_0=24 +x_0=6375000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    }
});

await converter.convertFiles('../data/lod2/updated-tartu.gml', './public/model/');