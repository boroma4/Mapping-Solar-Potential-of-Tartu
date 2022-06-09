# Mapping Solar Potential of Tartu (and beyond)

## Description

This project was developed as a prototype of a tool to visualize solar potential of Estonian cities.

It was designed to work with the data from [Estonian Land Board](https://geoportaal.maaamet.ee/eng/Download-3D-data-p837.html).

Currently the [PVGIS API](https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service_en
) is used as a backend for estimating solar power, in the future this might change to a ML model.

## Demo

Available at http://172.17.65.121:3000/ (UT network).

## Setup

Please find setup scripts in `scripts/<os>/` to install needed environment. !Full-setup is meant to be used for clean machines.

## Running the pipeline

Please use `./scripts/<os>/run-pipe.sh <filename>` to run the pipeline with default parameters. Feel free to modify it for your needs.

Run `python3 pipeline/main.py --help` to see the full list of parameters supported and their descriptions.

## Running the web app

After running the pipeline run `./scripts/web.sh` to launch the web app. 
Please do not run the app directly as there is an important preprocessing step done in the script.

## Requirements
* Python 3.9+
* Node.js 15+

