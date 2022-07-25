# Mapping Solar Potential of Tartu (and beyond)

## Description

This project was developed as a prototype of a tool to visualize solar potential of Estonian cities.

It was designed to work with the data from [Estonian Land Board](https://geoportaal.maaamet.ee/eng/Download-3D-data-p837.html).

Currently the [PVGIS API](https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service_en
) is used as a backend for estimating solar power, in the future this might change to a ML model.

## Demo

Available at http://172.17.65.121:3000/ (UT network).

## Local setup

Please find setup scripts in `scripts/<os>/` to install needed environment. Full-setup is meant to be used for clean machines.

## Running the pipeline

Please use `./scripts/<os>/run-pipe.sh <filename>` to run the pipeline with default parameters. Feel free to modify it for your needs.

Run `python3 pipeline/main.py --help` to see the full list of parameters supported and their descriptions.

### Running from Docker

Prerequisite: allow mounting of the data folder to Docker containers.

```
docker build -t pipeline -f Dockerfile.pipeline .
docker run -v <full-path-to-repo>/data:/app/data pipeline --filename delta.gml --<other-param> <other-value>
```


## Running the web app (automatically uses LOD2 data from /data/lod2)

After running the pipeline run `./scripts/web.sh` to launch the web app. 
Please do not run the app directly as there is an important preprocessing step done in the script.

### Running from Docker


```
docker build -t web -f Dockerfile.web .
docker run -p 3000:3000 web
```

## Requirements
* Python 3.9+
* Node.js 15+

