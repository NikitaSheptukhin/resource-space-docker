#!/bin/bash

export MACHINE_IP=$(hostname -I | awk '{print $1}')
echo $MACHINE_IP
docker compose up -d --build
