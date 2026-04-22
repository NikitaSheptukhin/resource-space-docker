#!/bin/bash

export MACHINE_IP=$(hostname -I | awk '{print $1}')
export RESOURCESPACE_HOST="http://${MACHINE_IP}:8000"
echo $MACHINE_IP
docker compose up -d --build
