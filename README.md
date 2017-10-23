
# CanDIG GA4GH and Keycloak Server Deployment Script

---

## Overview:

This script deploys two docker containers for the CanDIG project:

1. Keycloak authentication server 
2. Authorization branch CanDIG GA4GH application server

The servers are configured to be registered with one another and communicate with such that a user must authenticate with the GA4GH server through a login page using the username and password specified prior to using its REST API.

The source code can be found at:

[https://github.com/Bio-Core/candigDeploy](https://github.com/Bio-Core/candigDeploy)

---

## Requirements:

* Docker
* git
* Python 2.7+

---

## Execution:

To execute this script, run the deployer script in the root directory:

```
python deployer.py deploy
```

The script will fail if the IPs of both GA4GH Server and Keycloak Server at not set to the IPs of the interfaces through which they may be accessed. 

Ensure that the ports (which by default are 8000 and 8080) are free. 

---

## Command Line Arguments:

The command line program is able to take in arguments for deployment. 
The details of such command line arguments can be viewed using 
the -h or --help option:

```
python deployer.py --help
```

The command line options can modify the following variables:

| Variable                | Default                    | Description                                                                                      | 
|:----------------------- |:-------------------------- |:------------------------------------------------------------------------------------------------ |
| keycloakIP              | 127.0.0.1                  | The IP of the Keycloak server to listen on.                                                      | 
| ga4ghIP                 | 127.0.0.1                  | The IP of the GA4GH server to listen on.                                                         | 
| keycloakPort            | 8080                       | The port number the Keycloak server listens on.                                                  |
| ga4ghPort               | 8000                       | The port number of the Ga4gh server listens on.                                                  |
| ga4ghClientID           | ga4ghServer                | The Keycloak client id of the GA4GH server with which it will register with Keycloak as a client | 
| realmName               | CanDIG                     | The name of the Keycloak realm on which the GA4GH server registers as a client                   | 
| keycloakImageName       | keycloak_candig_server     | The name to assign the resulting Docker image of the Keycloak server                             |
| keycloakContainerName   | keycloak_candig_server     | The name to assign the container running the Keycloak server image                               |
| ga4ghImageName          | ga4gh_candig_server        | The name to assign the resulting Docker image of the GA4GH server                                |
| ga4ghContainerName      | ga4gh_candig_server        | The name to assign the container running the GA4GH server image                                  |
| AdminUsername           | admin                      | The username of the Keycloak administrator account                                               |
| UserUsername            | user                       | The username of the user to login to the GA4GH server at the login page                          |  
| override                | False                      | Overrides the target source directory for ga4gh  with a clean repository pulled from github      |
| ga4ghSrc                | ./ga4ghDocker/ga4gh-server | The location of the source directory to use for ga4gh                                            |


---


## Server Access and Login:

The GA4GH server can be accessed at GA4GH_IP:GA4GH_PORT 
and the Keycloak server can be accessed at KEYCLOAK_IP:KEYCLOAK_PORT 
where GA4GH_PORT is 8000 and KEYCLOAK_PORT is 8080 by default. 

On the master realm on the administration console for Keycloak, the administration account can be accessed with the defaults:

* username: admin
* password: admin

On the realmName realm (which has the name CanDIG by default), the user account can be accessed with the defaults:

* username: user
* password: user

Note the interface on which the software containers may be accessed. You may list the interfaces using a tool such as ip or ifconfig.
If the software containers are running with a software hypervisor, such as VirtualBox, you may have to listen on the interface dedicated 
to the virtual machine operating system, such as vboxnet0, instead of listening locally on loopback with localhost. 
