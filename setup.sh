echo "Installing python deps"
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r pipeline/requirements.txt
pip install autopep8


echo "Installing react app deps"
cd web-app
npm i
cd ..

echo "Installing Node.js deps"
cd pipelines/node_scripts
npm i