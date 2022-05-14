source venv/bin/activate

python3 pipeline/main.py solar --lod 2 --datapath data --filename luunja.gml --pv-efficiency 0.21 --pv-loss 0.14 --output-format tiles
cp data/lod2/luunja-output/* web-app/public
./client.sh