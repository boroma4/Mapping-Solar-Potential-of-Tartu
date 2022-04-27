source venv/bin/activate

python3 pipelines/main.py solar --lod 2 --datapath data --filename luunja.gml --pv-efficiency 0.21 --pv-loss 0.14
cp data/lod2/luunja-output/* web-app/public
./client.sh