source venv/bin/activate

autopep8 --in-place --aggressive --recursive --max-line-length 120 ./pipeline

cd web-app 
npm run lint
cd ..

cd pipeline/node_scripts
npm run lint
cd ../..
