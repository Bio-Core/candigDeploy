#!/bin/bash

# configure the IP from which to access keycloak and ga4gh from the host
KEYCLOAK_IP="192.168.99.100"
GA4GH_IP=${KEYCLOAK_IP}

# the ports on which to find the keycloak and ga4gh server from the host
KEYCLOAK_PORT="8080"
GA4GH_PORT="8000"

# ga4gh client id and realm name on which ga4gh will be registed
GA4GH_CLIENT_ID=ga4ghServer
GA4GH_REALM_NAME=CanDIG

# the image and container name for the keycloak server
KEYCLOAK_IMAGE_NAME=keycloak_candig_server
KEYCLOAK_CONTAINER_NAME=${KEYCLOAK_IMAGE_NAME}

# the image and container name for the ga4gh server
GA4GH_IMAGE_NAME=ga4gh_candig_server
GA4GH_CONTAINER_NAME=${GA4GH_IMAGE_NAME}

# the username and password of the administrator account 
# for the keycloak server on the master realm
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# the username and password of the user account
# for the keycloak server on the ga4gh realm
USER_USERNAME=user
USER_PASSWORD=user

SOURCE_DIR=$(pwd)
INIT_REPO="TRUE"

# usage function explaining how to use the program

display_usage() { 
    echo -e "\nUsage: dockerMaster [--ip IPADDRESS] [--keycloakIP IPADDRESS] [--ga4ghIP IPADDRESS]" 
    echo -e "       [--keycloakPort PORTNUMBER] [--ga4ghPort PORTNUMBER] [--realm REALMNAME] [--id CLIENTID]" 
    echo -e "       [--keycloakContainer NAME] [--ga4ghContainer NAME] [--keycloakImage TAG] [--ga4ghImage TAG]"
    echo -e "       [--adminName USERNAME] [--adminPass PASSWORD] [--userName USERNAME] [--userPass PASSWORD]\n"
    echo -e "-h, --help                display command line options"
    echo -e "-i, --ip                  set the ip address of both servers"
    echo -e "-k, --keycloakIP          set the ip address of the keycloak server"
    echo -e "-g, --ga4ghIP             set the ip address of the ga4gh server"
    echo -e "-p, --keycloakPort        set the port number of the keycloak server"
    echo -e "-o, --ga4ghPort           set the port number of the ga4gh server"
    echo -e "-r, --realm               set the keycloak realm name"
    echo -e "-d, --id                  set the ga4gh server client id"
    echo -e "    --keycloakContainer   set the keycloak container name"
    echo -e "    --ga4ghContainer      set the ga4gh server container name"
    echo -e "    --keycloakImage       set the keycloak image tag"
    echo -e "    --ga4ghContainer      set the ga4gh container tag"
    echo -e "-a, --adminName           set the administrator account username"
    echo -e "    --adminPass           set the administrator account password" 
    echo -e "-n, --userName            set the user account username"
    echo -e "-p, --userPass            set the user account password\n"
} 

# parse the optional command line arguments

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -k|--keycloakIP)
    KEYCLOAK_IP="$2"
    shift # past argument
    shift # past value
    ;;
    -g|--ga4ghIP)
    GA4GH_IP="$2"
    shift # past argument
    shift # past value
    ;;
    -i|--ip)
    KEYCLOAK_IP="$2"
    GA4GH_IP=${KEYCLOAK_IP}
    shift
    shift
    ;;
    -p|--keycloakPort)
    KEYCLOAK_PORT="$2"
    shift # past argument
    shift # past value
    ;;
    -o|--ga4ghPort)
    GA4GH_PORT="$2"
    shift
    shift
    ;;
    -r|--realm)
    GA4GH_REALM_NAME="$2"
    shift
    shift
    ;;
    -d|--id)
    GA4GH_CLIENT_ID="$2"
    shift
    shift
    ;;
    --keycloakContainer)
    KEYCLOAK_CONTAINER_NAME="$2"
    shift
    shift
    ;;
    --ga4ghContainer)
    GA4GH_CONTAINER_NAME="$2"
    shift
    shift
    ;;
    --keycloakImage)
    KEYCLOAK_IMAGE_NAME="$2"
    shift
    shift
    ;;
    --ga4ghImage)
    GA4GH_IMAGE_NAME="$2"
    shift
    shift
    ;;
    --adminName)
    ADMIN_USERNAME="$2"
    shift
    shift
    ;;
    --adminPass)
    ADMIN_PASSWORD="$2"
    shift
    shift
    ;;
    --userName)
    USER_USERNAME="$2"
    shift
    shift
    ;;
    --userPass)
    USER_PASSWORD="$2"
    shift
    shift
    ;;
    -h|--help)
    display_usage
    exit 0
    shift # past argument
    ;;
    *)    # unknown option
    display_usage
    exit 1
    #POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# clean up any duplicate containers currently running or stopped

docker container kill ${KEYCLOAK_CONTAINER_NAME} ${GA4GH_CONTAINER_NAME}
docker container rm ${KEYCLOAK_CONTAINER_NAME} ${GA4GH_CONTAINER_NAME}

# build the keycloak server

KEYCLOAK_DIR="./keycloakDocker"

GA4GH_DIR="./ga4ghDocker"

docker build -t ${KEYCLOAK_IMAGE_NAME} --build-arg ga4ghIp=${GA4GH_IP} \
--build-arg adminUsername=${ADMIN_USERNAME} --build-arg adminPassword=${ADMIN_PASSWORD} \
--build-arg realmName=${GA4GH_REALM_NAME} --build-arg clientId=${GA4GH_CLIENT_ID} \
--build-arg userUsername=${USER_USERNAME} --build-arg userPassword=${USER_PASSWORD} \
--build-arg ga4ghPort=${GA4GH_PORT} ${KEYCLOAK_DIR}

# run the keycloak server

docker run -p ${KEYCLOAK_PORT}:8080 --name ${KEYCLOAK_CONTAINER_NAME} ${KEYCLOAK_IMAGE_NAME} & 

# initialize the http request settings

HTTPRESULT=404
TIMEOUT=60
COUNTER=0

# Send HTTP requests to the server 
# to determine if the server has been deployed 
# if the server returns the result http 200, 
# it is deployed   
# exit the loop upon HTTP 200 or when the counter times out
# the counter is used to prevent an infinite loop
# the program will crash if the server is not accessible by this time

while [ $HTTPRESULT -ne 200 -a $COUNTER -le $TIMEOUT ]; do
    HTTPRESULT=$(curl -s -o /dev/null -w "%{http_code}" \
    http://${KEYCLOAK_IP}:${KEYCLOAK_PORT})
    let "COUNTER++"
    sleep 2
done

# extract the client secret to configure ga4gh with

SECRET_FILE="/home/secret.txt"

SECRET=$(docker exec ${KEYCLOAK_CONTAINER_NAME} cat ${SECRET_FILE})

echo "SECRET:"
echo ${SECRET}

# remove the secret file

docker exec ${KEYCLOAK_CONTAINER_NAME} rm "${SECRET_FILE}"

#SOURCE_DIR="."
#INIT_REPO="TRUE"

#GA4GH_DIR

#echo "GA4GH_DIR"

#echo "${GA4GH_DIR}"


#BASE_DIR=$(dirname "${0}")

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ${BASE_DIR}

INIT_DIR="${BASE_DIR}/ga4ghDocker/ga4ghInitRepo.sh" 





echo "${INIT_DIR}"

#echo $(pwd)



if [ "${INIT_REPO}" == "TRUE" ]; then 
    $(chmod +x "${INIT_DIR}")
    $(bash -c "${INIT_DIR} ${SOURCE_DIR}/ga4gh-server")
fi



# use the directory containing the GA4GH build scripts and code
#GA4GH_DIR="./ga4ghDocker/"

# build the ga4gh server

#echo "SOURCE"
#echo "${SOURCE_DIR}"

#SOURCE_DIR_DOCKER=""

docker build -t ${GA4GH_IMAGE_NAME} --build-arg clientSecret=${SECRET} --build-arg keycloakIp=${KEYCLOAK_IP} --build-arg clientIp=${GA4GH_IP} --build-arg clientId=${GA4GH_CLIENT_ID} --build-arg realmName=${GA4GH_REALM_NAME}  --build-arg keycloakPort=${KEYCLOAK_PORT} --build-arg ga4ghPort=${GA4GH_PORT} --build-arg sourceDir="ga4gh-server" "${GA4GH_DIR}"

# run the ga4gh server

docker run -p ${GA4GH_PORT}:80 --name ${GA4GH_CONTAINER_NAME} ${GA4GH_IMAGE_NAME} &

# print the login information

echo
echo "Deployment Complete."
echo
echo "Keycloak is accessible at:"
echo "IMAGE:     "${KEYCLOAK_IMAGE_NAME}
echo "CONTAINER: "${KEYCLOAK_CONTAINER_NAME}
echo "IP:PORT:   "${KEYCLOAK_IP}":"${KEYCLOAK_PORT}
echo
echo "GA4GH Server is accessible at:"
echo "IMAGE:     "${GA4GH_IMAGE_NAME}
echo "CONTAINER: "${GA4GH_CONTAINER_NAME} 
echo "IP:PORT:   "${GA4GH_IP}":"${GA4GH_PORT}
echo 
echo "User Account:"
echo "USERNAME:  "${USER_USERNAME}
echo "PASSWORD:  "${USER_PASSWORD}
echo
echo "Admin Account:"
echo "USERNAME:  "${ADMIN_USERNAME}
echo "PASSWORD:  "${ADMIN_PASSWORD}
echo

exit 0 
