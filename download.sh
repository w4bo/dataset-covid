#!/bin/bash
set -exo
cd libs
if [ ! -f "instantclient-basic-linux.x64-21.1.0.0.0.zip" ]; then 
    curl -k -o instantclient-basic-linux.x64-21.1.0.0.0.zip https://big.csr.unibo.it/projects/nosql-datasets/instantclient-basic-linux.x64-21.1.0.0.0.zip
    unzip instantclient-basic-linux.x64-21.1.0.0.0.zip
    chmod -R 777 instantclient_21_1
    pwd
fi
ls -las
cd -