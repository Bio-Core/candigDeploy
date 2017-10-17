#!/bin/bash

# sets up keycloak to listen on the external eth0 IP

# find the external inet IP address for the eth0 interface
# discard the localhost (127.0.0.1) result

IP_ADDR=$(ip addr | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' \
| grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')

# start the keycloak server to listen on the external IP address

echo ${IP_ADDR}

/home/keycloak-3.3.0.CR2/bin/standalone.sh -b ${IP_ADDR}

