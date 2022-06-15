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

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}

for f in *.ipynb
do 
  echo "Processing $f file...";
  jupyter nbconvert --execute --to notebook --inplace $f
  jupyter nbconvert --to script $f
  extension="${f##*.}"
  filename="${f%.*}"
  ipython $filename.py
done

java -cp libs/COOL-all.jar it.unibo.conversational.database.DBreader --dbms ${ORACLE_DBMS} --user ${ORACLE_USER} --pwd ${ORACLE_PWD} --ip ${ORACLE_IP} --port ${ORACLE_PORT} --db ${ORACLE_DB} --ft ${ORACLE_FT}

touch datasets/.pythonready

until [ -f datasets/COVID_WEEKLY.DMP ]
do
  sleep 1
done

ls -las datasets