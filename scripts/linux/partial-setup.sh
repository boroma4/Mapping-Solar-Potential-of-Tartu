
python3.9 -m venv venv

echo "Installing python deps"
source venv/bin/activate
pip3.9 install -r pipeline/requirements.txt
pip3.9 install autopep8

echo "Installing react app deps"
cd web-app
npm i
cd ..

echo "Installing Node.js deps"
cd pipeline/node_scripts
npm i

echo "install screen"
sudo apt install screen