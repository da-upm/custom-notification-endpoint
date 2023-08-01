#!/bin/bash

if [ "$EUID" -ne 0 ] 
    then echo "Para poder realizar el despliegue, debes ejecutar este script como root."
	exit
fi

docker build -t cne .
docker run -d --mount type=bind,src=./data,dst=/srv/data --name cne cne