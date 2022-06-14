#!/bin/bash
set -xo
rm datasets/.ready
rm datasets/.pythonready
rm datasets/COVID_WEEKLY.DMP
docker-compose down