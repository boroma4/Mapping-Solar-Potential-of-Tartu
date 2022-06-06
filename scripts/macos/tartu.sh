source venv/bin/activate

python3 pipeline/main.py --lod 2 --filename tartu.gml --pv-efficiency 0.21 --pv-loss 0.14 --roof-coverage 0.90 --optimize-2d true --output-format tiles

cp data/lod2/tartu-output/* web-app/public/