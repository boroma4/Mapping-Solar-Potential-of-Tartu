echo "Installing python deps"
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip3 install -r pipeline/requirements.txt
pip3 install autopep8


echo "Installing react app deps"
cd web-app
npm i
cd ..

echo "Installing Node.js deps"
cd pipeline/node_scripts
npm i