source venv/bin/activate

CITY=$1

python3.9 pipeline/main.py --lod 2 --filename $CITY.gml --pv-efficiency 0.21 --pv-loss 0.14 --roof-coverage 0.90 --optimize-2d true --output-format tiles

echo "Removing files from web-app/public and copying results there"
rm web-app/public/*
cp data/lod2/$CITY-output/* web-app/public/