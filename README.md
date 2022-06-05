# Mapping Solar Potential of Tartu (and beyond)

## Description

This project was developed as a prototype of a tool to visualize solar potential of Estonian cities.

It was designed to work with the data from [Estonian Land Board](https://geoportaal.maaamet.ee/eng/Download-3D-data-p837.html).

Currently the [PVGIS API](https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service_en
) is used as a backend for estimating solar power, in the future this might change to a ML model.

## Setup

Please use `setup.sh` script to install needed environment.

## Running the pipeline

Please take a look at `tartu.sh` script which should give you an idea how to run the estimation pipeline.

Run `python3 pipeline/main.py --help` to see the full list of parameters supported and their descriptions.

## Running the web app

Currently the web app can only be ran locally. Please place the output files from the pipeline in the `web-app/public` and then run `client.sh` script.

## Tech stack 
* Python 3
* Node.js 
* React
* Cesium
* Vite

## Requirements
* Python 3.9+
* Node.js 15+

