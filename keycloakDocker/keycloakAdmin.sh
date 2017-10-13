#!/bin/bash

ADMIN_USERNAME=${1}
ADMIN_PASSWORD=${2}
REALM_NAME=${3}
CLIENT_ID=${4}
GA4GH_IP=${5}
USER_USERNAME=${6}
USER_PASSWORD=${7}
GA4GH_PORT=${8}

# Create the admin account
/home/keycloak-3.3.0.CR2/bin/add-user-keycloak.sh --user=$ADMIN_USERNAME \
--password=$ADMIN_PASSWORD

# Start the keycloak server on localhost:8080 in Detached mode
/home/keycloak-3.3.0.CR2/bin/standalone.sh &

PINGRESULT=1
TIMEOUT=100
COUNTER=0

# Send HTTP requests to  the server to determine if the server has been deployed
# if the server results http 200, it is deployed

# keycloak is accessed locally for initial configuration
# the IP and port should be fixed to localhost at 8080

while [ $PINGRESULT -ne 200 -a $COUNTER -le $TIMEOUT ]; do
    PINGRESULT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
    let "COUNTER++" 
    sleep 2
done

# login as admin
/home/keycloak-3.3.0.CR2/bin/kcadm.sh config credentials \
--server http://localhost:8080/auth --realm master \
--user ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD}

# Create a realm with name REALM_NAME
/home/keycloak-3.3.0.CR2/bin/kcadm.sh create realms \
-s realm=${REALM_NAME} -s enabled=true

# Create a client with client id CLIENT_ID
CLIENT_ID_KEYCLOAK=$(/home/keycloak-3.3.0.CR2/bin/kcadm.sh \
create clients -r ${REALM_NAME} -s clientId=${CLIENT_ID} -s enabled=true -i)

# Configure the client with redirect uri http://localhost:8000/* and as baseUrl and adminUrl
/home/keycloak-3.3.0.CR2/bin/kcadm.sh update clients/${CLIENT_ID_KEYCLOAK} \
-r ${REALM_NAME} -s "redirectUris=[\"http://${GA4GH_IP}:${GA4GH_PORT}/*\"]" \
-s baseUrl=http://${GA4GH_IP}:${GA4GH_PORT}/* -s adminUrl=http://${GA4GH_IP}:${GA4GH_PORT}/* -s publicClient=false

# Create a user
USER_ID=$(/home/keycloak-3.3.0.CR2/bin/kcadm.sh create users -r ${REALM_NAME} \
-s username=${USER_USERNAME} -s enabled=true -i)

# reset the password
echo ${USER_PASSWORD} | /home/keycloak-3.3.0.CR2/bin/kcadm.sh set-password \
-r ${REALM_NAME} --userid ${USER_ID}

SECRET_FILE="secret.txt"

# get the adapter configuration for the ga4gh client
/home/keycloak-3.3.0.CR2/bin/kcadm.sh get clients/${CLIENT_ID_KEYCLOAK}/installation/providers/keycloak-oidc-jboss-subsystem \
-r ${REALM_NAME} > ${SECRET_FILE}

# parse the client secret
SECRET=$(xmllint --xpath "string(/secure-deployment/credential)" ${SECRET_FILE})

# save the client secret to the file
# the file is extracted during the docker initialization of the ga4gh server
echo ${SECRET} > ${SECRET_FILE}

exit 0
