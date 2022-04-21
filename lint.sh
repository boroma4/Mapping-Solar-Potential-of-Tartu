pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install autopep8

autopep8 --in-place --aggressive --recursive --max-line-length 120 ./pipelines
