#!/bin/bash

tokenTracer=${1}

# sets up keycloak to listen on the external eth0 IP

# find the external inet IP address for the eth0 interface
# discard the localhost (127.0.0.1) result

IP_ADDR=$(ip addr | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' \
| grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')

BASE_DIR=$(dirname "$0")

CONFIG_FILENAME="keycloakConfig.json"
CONFIG_FILE="${BASE_DIR}/${CONFIG_FILENAME}"

# start the keycloak server to listen on the external IP address

#echo ${IP_ADDR}

echo "keycloakStart tokenTracer:"
echo ${1}

if [ ${tokenTracer} == "True" ]
then
    echo "tokenTracer"
    /srv/keycloak-3.3.0.CR2/bin/standalone.sh -b ${IP_ADDR} -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file="${CONFIG_FILE}" -Dkeycloak.migration.strategy=OVERWRITE_EXISTING &
    /usr/bin/python /srv/tokenTracer/pyparseLive.py
else
    echo "No tracing"
    /srv/keycloak-3.3.0.CR2/bin/standalone.sh -b ${IP_ADDR} -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file="${CONFIG_FILE}" -Dkeycloak.migration.strategy=OVERWRITE_EXISTING 
fi