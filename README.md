# Mapping Solar Potential of Tartu (and beyond)

## Building data obtained from

https://geoportaal.maaamet.ee/eng/Download-3D-data-p837.html

## API for simulating PV systems

https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service_en

## Project structure

* **cesium-prototype-js** - temporary web app to view the results
* **preprocessor** - computes useful roof attributes from CityGML data
* **server** - API that does estimations of solar potential for buldings based on precomputed data and PVGIS API