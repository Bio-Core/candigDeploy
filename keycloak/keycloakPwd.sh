#!/bin/bash

USER_FLAG=${1}
USER_PASSWORD=${2}
ADMIN_FLAG=${3}
ADMIN_PASSWORD=${4}
IP_ADDRESS=${5}
ORIG_ADMIN_PASSWORD=${6}
ADMIN_USERNAME=${7}
USER_USERNAME=${8}
REALM_NAME=${9}

/srv/keycloak-3.3.0.CR2/bin/kcadm.sh config credentials --server http://${IP_ADDRESS}:8080/auth --realm master --user ${ADMIN_USERNAME} --password ${ORIG_ADMIN_PASSWORD}

if [ ${USER_FLAG} == "True" ]
then
    echo ${USER_PASSWORD} | /srv/keycloak-3.3.0.CR2/bin/kcadm.sh set-password -r ${REALM_NAME} --username ${USER_USERNAME}
fi
if [ ${ADMIN_FLAG} == "True" ] 
then
    echo ${ADMIN_PASSWORD} | /srv/keycloak-3.3.0.CR2/bin/kcadm.sh set-password -r master --username ${ADMIN_USERNAME}
fi

exit 0 