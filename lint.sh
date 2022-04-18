pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

autopep8 --in-place --aggressive --recursive --max-line-length 120 ./preprocessor
autopep8 --in-place --aggressive --recursive --max-line-length 120 ./server