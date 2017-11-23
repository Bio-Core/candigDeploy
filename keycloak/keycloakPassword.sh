#!/bin/bash

# resets the user and admin password to be the passwords specified by the deployer script
IP_ADDRESS=${1}
REALM_NAME=${2}
ADMIN_USERNAME=${3}
ADMIN_PASSWORD=${4}
USER_USERNAME=${5}
USER_PASSWORD=${6}

# reset the passwords if they are not the default
if [ \( "${USER_PASSWORD}" != "user" \) -o \( "${ADMIN_PASSWORD}" != "admin" \) ]
then
    TIMEOUT=50
    COUNTER=0
    REQUEST=404

    while [ ${REQUEST} -ne 200 -a ${COUNTER} -le ${TIMEOUT} ]
    do
	REQUEST=$(curl -s -o /dev/null -w "%{http_code}" http://"${IP_ADDR}":8080)
	let "COUNTER++"
	sleep 2
    done

    /srv/keycloak-3.4.0.Final/bin/kcadm.sh config credentials --server http://${IP_ADDRESS}:8080/auth --realm master --user ${ADMIN_USERNAME} --password admin

    if [ "${USER_PASSWORD}" != "user" ]
    then
        echo ${USER_PASSWORD} | /srv/keycloak-3.4.0.Final/bin/kcadm.sh set-password -r ${REALM_NAME} --username ${USER_USERNAME}
    fi

    if [ "${ADMIN_PASSWORD}" != "admin" ]
    then
        echo ${ADMIN_PASSWORD} | /srv/keycloak-3.4.0.Final/bin/kcadm.sh set-password -r master --username ${ADMIN_USERNAME}
    fi
fi

exit 0




