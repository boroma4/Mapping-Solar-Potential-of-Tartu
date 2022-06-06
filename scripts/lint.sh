source venv/bin/activate

echo "Linting pipeline"
autopep8 --in-place --aggressive --recursive --max-line-length 120 ./pipeline

echo "Linting web app"
cd web-app 
npm run lint
cd ..

