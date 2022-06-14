#!/bin/bash
set -exo

chmod -R 777 /data
ls -las /data

# impdp covid_weekly/oracle@127.0.0.1:1521/xe DIRECTORY=ORACLE_DUMP DUMPFILE=COVID_WEEKLY.DMP SCHEMAS=covid_weekly

touch /data/.ready

until [ -f /data/.pythonready ]
do
     sleep 1
done

expdp covid_weekly/oracle@xe directory=oracle_dump dumpfile=covid_weekly.dmp SCHEMAS=covid_weekly