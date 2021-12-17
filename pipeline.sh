#/bin/bash

echo "this script is still WIP"
echo "starting the preprocessing"

pip install -r ./Preprocessing/gml/requirements.txt

echo "adding area attribute (roof area) to CityGML buildings"
python3 ./Preprocessing/gml/parse.py /Data/citygml/lod1-tartu.gml

echo "TODO: converting CityGML to 3D tiles"

echo "launching the server"
cd Cesium && npm i && npm start
