#!/bin/bash
set -e
set -xo
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

./stop.sh
docker-compose up --build -d --remove-orphans

until [ -f datasets/.ready ]
do
     sleep 1
done

for f in *.ipynb
do 
  echo "Processing $f file...";
  jupyter nbconvert --execute --to notebook --inplace $f
  jupyter nbconvert --to script $f
  extension="${f##*.}"
  filename="${f%.*}"
  ipython $filename.py
done

touch datasets/.pythonready