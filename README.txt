//////////////////////////////////////////////

CanDIG GA4GH+Keycloak Server Deployment Script

//////////////////////////////////////////////

OVERVIEW:

This script deploys two docker containers, one containing a keycloak server, 
and other containing the authorization branch CanDIG GA4GH server. The 
servers are configured to  be registered with one another and communicate 
with each other such that a user can login to the GA4GH server through a 
login page using the username and password specified in the shell script.

REQUIREMENTS:

This script requires a distribution of Docker to work and a bash shell.

EXECUTION:

To execute this script, run:

./dockerMaster.sh

which is located in the keycloak directory

The script will fail if the KEYCLOAK_IP variable is not set to the IP of the 
docker virtual machine on which the docker containers will reside.

PARAMETERIZATION:

The script can be reparameterized as follows by changing the variables 
declared at the beginning of the dockerMaster.sh:

KEYCLOAK_IP             - The IP of the Keycloak server to listen on. 
GA4GH_IP                - The IP of the GA4GH server to listen on.
GA4GH_CLIENT_ID         - The Keycloak client id of the GA4GH server with 
                          which it will register with Keycloak as a client
GA4GH_REALM_NAME        - The name of the Keycloak realm on which the GA4GH 
                          server registers as a client
KEYCLOAK_IMAGE_NAME     - The name to assign the resulting Docker image of 
                          the Keycloak server
KEYCLOAK_CONTAINER_NAME - The name to assign the container running the 
                          Keycloak server image
GA4GH_IMAGE_NAME        - The name to assign the resulting Docker image of 
                          the GA4GH server
GA4GH_CONTAINER_NAME    - The name to assign the container running the GA4GH 
                          server image
ADMIN_USERNAME          - The username of the Keycloak administrator account 
ADMIN_PASSWORD          - The password of the Keycloak administrator account
USER_USERNAME           - The username of the user to login to the GA4GH 
                          server at the login page
USER_PASSWORD           - The password of the user to login to the GA4GH 
                          server at the login page

SERVER ACCESS:

The GA4GH server can be accessed at GA4GH_IP:GA4GH_PORT 
The Keycloak server can be accessed at KEYCLOAK_IP:KEYCLOAK_PORT
Where GA4GH_PORT is 8000 and KEYCLOAK_PORT is 8080 by default 


