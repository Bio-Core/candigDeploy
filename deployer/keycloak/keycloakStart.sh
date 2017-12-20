#!/bin/bash

#tokenTracer=
#REALM_NAME=
#ADMIN_USERNAME
#ADMIN_PASSWORD=${4}
#USER_USERNAME=${5}
#USER_PASSWORD=${6}

# sets up keycloak to listen on the external eth0 IP

# find the external inet IP address for the eth0 interface
# discard the localhost (127.0.0.1) result

IP_ADDR=$(ip addr | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' \
| grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep -v '^10..*')

BASE_DIR=$(dirname "$0")

CONFIG_FILENAME="keycloakConfig.json"
CONFIG_FILE="${BASE_DIR}/${CONFIG_FILENAME}"

# start the keycloak server to listen on the external IP address

#/srv/keycloakPassword.sh ${IP_ADDR} ${REALM_NAME} ${ADMIN_USERNAME} ${ADMIN_PASSWORD} ${USER_USERNAME} ${USER_PASSWORD} &

# run the token tracer if specified
if [ "${tokenTracer}" == "True" ]
then    
    /usr/bin/python /srv/tokenTracer/tokenTracer/tracer.py &
fi

# /srv/keycloak-3.4.0.Final/bin/standalone.sh -b ${IP_ADDR} -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file="${CONFIG_FILE}" -Dkeycloak.migration.strategy=OVERWRITE_EXISTING 

/srv/keycloak/bin/standalone.sh -b ${IP_ADDR} -Dkeycloak.migration.action=import -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.file="${CONFIG_FILE}" -Dkeycloak.migration.strategy=OVERWRITE_EXISTING


exit 0






