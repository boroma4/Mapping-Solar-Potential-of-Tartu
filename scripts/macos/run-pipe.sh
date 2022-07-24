source venv/bin/activate

CITY=$1

python3 pipeline/main.py --lod 2 --filename ${CITY}.gml --pv-efficiency 0.21 --pv-loss 0.14 --roof-coverage 0.90 --optimize-2d true --output-format tiles --node-ram-limit 5500
