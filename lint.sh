pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

autopep8 --in-place --aggressive --recursive ./preprocessor
autopep8 --in-place --aggressive --recursive ./server