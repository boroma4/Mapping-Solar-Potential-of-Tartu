
echo "installing Node.js 16"
curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -
sudo apt -y install nodejs

echo "installing python 3.9"
sudo apt install python3.9-venv
sudo apt install python3.9-pip

python3 -m venv venv

echo "Installing python deps"
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