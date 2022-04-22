pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r pipelines/requirements.txt

python3 pipelines/main.py solar --lod 2 --datapath data --filename tartu.gml