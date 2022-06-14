#!/bin/bash
set -exo

if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

./stop.sh
docker-compose up --build -d --remove-orphans

until [ -f datasets/.ready ]
do
     sleep 1
done

export LD_LIBRARY_PATH=${ORACLE_PATH}

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

until [ -f datasets/COVID_WEEKLY.DMP ]
do
     sleep 1
done