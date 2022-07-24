CITY=$1

echo "Removing files from web-app/cities/${CITY} and copying results there"
mkdir -p cities/$CITY
rm cities/$CITY/*
cp ../data/lod2/$CITY-output/* cities/$CITY/