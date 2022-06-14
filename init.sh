#!/bin/bash
set -exo

echo "Replacing .env.example with .env"
cp .env.example .env

P=$(pwd)
echo $P

if [ -d "venv" ] 
then
    echo "The virtual environment already exists" 
else
    echo "Creating the virtual environment" 
    python -m venv venv
    if [ -d "venv/bin" ]
    then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
    pip install -r requirements.txt
    chmod -R 777 .
    cd -
fi

sed -i "s+\!HOME\!+${P}+g" .env
echo "Done."