#/bin/bash


pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt


python3 run.py
cd Cesium
npm run gen && npm start