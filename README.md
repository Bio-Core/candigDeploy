
# CanDIG GA4GH and Keycloak Server Deployment Script

---

## Overview:

This script deploys application servers for the CanDIG project:

1. Keycloak authentication server 
2. Authorization branch CanDIG GA4GH application server

The deployment can be faciliated either through Docker, Singularity, or Vagrant.

The servers are configured to be registered with one another and communicate with such that a user must authenticate with the GA4GH server through a login page using the username and password specified prior to using its REST API.

In each deployment, the Keycloak server is essential, as it provides login and authentication facilities for each application server that is available to the deployment program.

The deployer also supports:

* The loading of test data onto the GA4GH server
* Execution of a token tracer debugging program
* Deployment of a Keycloak-authenticated Funnel application server

The source code can be found at:

[https://github.com/Bio-Core/candigDeploy](https://github.com/Bio-Core/candigDeploy)

---

## Requirements:

* Linux OR MacOS
* Docker OR Vagrant OR Singularity
* git
* Python 2.7+

Note that Singularity will NOT work on MacOS, and hence requires the Vagrant deployment to use Singularity. 

Docker or Vagrant may need a hypervisor such as VirtualBox in order to work.

---

## Execution:

To execute this script, run the deployer script in the root directory:

```
python deployer.py deploy
```

The script will fail if the IPs of both GA4GH Server and Keycloak Server at not set to the IPs of the interfaces through which they may be accessed. 

Ensure that the ports (which by default are 8000 and 8080) are free. The docker daemon must be running in order for Docker deployment to work.


### Vagrant Deployment Issues

If the Vagrant containers fail to be removed, delete processes associated with Vagrant using `ps -e` and `kill PID`. 
You should look for processes under VBox, such as VBoxHeadless and delete those:

```ps -e | egrep VBox```

These processes may also be running vagrant itself or ruby:

```ps -e | egrep ruby|vagrant```

---

## Command Line Arguments:

The command line program is able to take in arguments for deployment. 
The details of such command line arguments can be viewed using 
the -h or --help option:

```
python deployer.py --help
```

The command line options can modify the following variables:

| Argument (Long Form)    | Short Form | Default                     | Description                                                                                      | 
|:----------------------- |:---------- |:--------------------------- |:------------------------------------------------------------------------------------------------ |
| ip                      | i          | None                        | The IP to assign all servers to listen on. Overrides all other IP settings.                      |
| keycloak-ip             | kip        | 127.0.0.1                   | The IP of the Keycloak server to listen on.                                                      | 
| ga4gh-ip                | gip        | 127.0.0.1                   | The IP of the GA4GH server to listen on.                                                         | 
| keycloak-port           | kp         | 8080                        | The port number the Keycloak server listens on.                                                  |
| ga4gh-port              | gp         | 8000                        | The port number of the Ga4gh server listens on.                                                  |
| ga4gh-id                | gid        | ga4gh                       | The Keycloak client id of the GA4GH server with which it will register with Keycloak as a client | 
| realm-name              | r          | CanDIG                      | The name of the Keycloak realm on which the GA4GH server registers as a client                   | 
| keycloak-image-name     | kin        | keycloak_candig_server      | The name to assign the resulting Docker image of the Keycloak server                             |
| keycloak-container-name | kcn        | keycloak_candig_server      | The name to assign the container running the Keycloak server image                               |
| ga4gh-image-name        | gin        | ga4gh_candig_server         | The name to assign the resulting Docker image of the GA4GH server                                |
| ga4gh-container-name    | gcn        | ga4gh_candig_server         | The name to assign the container running the GA4GH server image                                  |
| admin-username          | au         | admin                       | The username of the Keycloak administrator account                                               |
| user-username           | uu         | user                        | The username of the user to login to the GA4GH server at the login page                          |  
| override                | o          | False                       | Overrides the target source directory for ga4gh  with a clean repository pulled from github      |
| ga4ghSrc                | gs         |  ./ga4ghDocker/ga4gh-server | The location of the source directory to use for ga4gh                                            |
| singularity             | s          | False                       | Deploys GA4GH and Keycloak servers on Singularity                                                |
| token-tracer            | t          | False                       | Deploys the token tracer on the Keycloak server container (Docker only)                          |
| funnel                  | f          | False                       | Deploys the funnel server in addition to GA4GH and keycloak (Docker only)                        |
| no-data                 | nd         | False                       | Deploys the GA4GH server with no data loaded (Docker only)                                       |
| extra-data              | ed         | False                       | Deploys the GA4GH server with additional 1000g data (Docker only)                                |
| ga4gh-secret            | cs         | SEE CONFIGURATION           | The client secret for the GA4GH server                                                           |
| funnel-ip               | fip        | 127.0.0.1                   | The IP on which the funnel server is located                                                     |
| funnel-port             | fp         | 3002                        | The port number on which funnel listens                                                          |
| funnel-id               | fid        | funnel                      | The funnel client id for registration with Keycloak                                              |
| funnel-container-name   | fcn        | funnel_candig_server        | The container name of the funnel Docker container                                                |
| funnel-image-name       | fin        | funnel_candig_server        | The tag of the funnel Docker image name                                                          |
| funnel-secret           | fs         | SEE CONFIGURATION           | The client secret for the funnel server                                                          |
| vagrant                 | v          | False                       | Deploys a Vagrant container linked to the deployer on which Singularity containers may be deployed |
| vagrant-ip              | vip        | 127.0.0.1                   | The IP address of the Vagrant container                                                          | 

---

As by convention, long form arguments are given with the double hyphen prefix "--" and short form arguments are given a single hyphen "-", as seen in the examples. 

## Server Access and Login:

The GA4GH server can be accessed at `ga4gh-ip:ga4gh-port` (default: 127.0.0.1:8000)
and the Keycloak server can be accessed at `keycloak-ip:keycloak-port` (default: 127.0.0.1:8080).

On the master realm on the administration console for Keycloak, the administration account can be accessed with the defaults:

* username: admin
* password: admin

On the realmName realm (default: CanDIG), the user account can be accessed with the defaults:

* username: user
* password: user

Note the interface on which the software containers may be accessed. You may list the interfaces using a tool such as ip (with `ip addr`) or ifconfig.
If the software containers are running with a software hypervisor, such as VirtualBox, you may have to listen on the interface dedicated 
to the virtual machine operating system, such as vboxnet0, instead of listening locally on loopback with localhost. 

For instance, if you are running Docker using docker-machine with a software-based VirtualBox hypervisor, you can determine the IP address on which to set the deployment script using ip addr:

```
$ ip addr

lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
     inet 127.0.0.1/8 lo0
     inet6 ::1/128
     inet6 fe80::1/64 scopeid 0x1
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
     ether 01:2a:bc:34:5d:e6
     inet6 ab01::cd2:34ef:4gh5:ij67/89 secured scopeid 0x1
     inet 123.4.56.789/12 brd 123.4.56.789 en0
vboxnet0: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> mtu 1500
	  ether 0a:00:12:00:00:00
	  inet 192.168.12.1/12 brd 192.168.12.123 vboxnet0
```

You would then set the deployer to configure GA4GH and Keycloak to listen on 192.168.12.1, the IP address found in the inet field for the vboxnet0 interface:

```
python deployer.py -i 192.168.12.1 deploy
```

The deployer program will create a source code directory for GA4GH if one does not exist. It will reuse this source code in subsequent deployments, and reconfigure it based on the options provided. 

The --override option can be used to wipe the current source code directory with a default build:

```
python deployer.py -o deploy
```

The override option will replace the existing source code directory with a new one pulled from git. It is recommended that you use a copy of the source code that you are modifying for development purposes, as this will destroy all of your work. 

### Private IP Addresses

When deploying through VirtualBox or any software hypervisor, the ip addresses assigned as an interface must be within the private range of IP addresses. This is particularly relevant for Vagrant deployment if used with VirtualBox, where the vagrant IP address must be private. 

The private IP address range is as follows:

* 192.168.0.0 – 192.168.255.255
* 172.16.0.0 – 172.31.255.255
* 10.0.0.0 – 10.255.255.255

---

## Examples

### Example 1: Keycloak and GA4GH Server Docker Deployment

To deploy Keycloak and GA4GH on separate Docker containers on localhost, invoke the script with no arguments:

```
python deployer.py deploy
```


### Example 2: Overriding the source configuration

To update the GA4GH source files (found in /ga4gh/ga4gh-server by default), use the --override option in the deployment. You cannot set options that configure GA4GH when an existing source code directory is being use unless you have this option. 

```
python deployer.py -o deploy
```


### Example 3: Keycloak and GA4GH Server Singularity/Vagrant Deployment

To deploy Keycloak and GA4GH on separate Singularity containers hosted on a single Vagrant container, use the --singularity option:

```
python deployer.py -s deploy
```

Both servers will automatically be set to have the IP address 192.168.12.123. The override is necessary to configure GA4GH with this setting.

### Example 4: Deployment on a different IP address

To deploy Keycloak and GA4GH server with different IP addresses use the --ip option. This will change both the Keycloak and GA4GH server IPs. The override option is needed to overwrite any existing configuration files set to a different IP for GA4GH.

```
python deployer.py -i 192.168.12.123 deploy
```

This will cause both servers to be configured on the IP address 192.168.12.123. GA4GH and Keycloak need to know each other's IP addresses in order for the authentication protocols to work. 

You can also change the ip ports that the Keycloak and GA4GH servers listen on individually through the keycloak-ip and ga4gh-ip options. These will be overrided by the --ip option if it is used.

```
python deployer.py -kip 127.123.45.678 deploy
```

This causes Keycloak to be assigned the IP address 127.123.45.678. For GA4GH, we can assign an IP 192.168.00.100:

```
python deployer.py -gip 192.168.00.100 deploy
```

We can also combine these arguments:

```
python deployer.py -kip 172.101.42.101 -gip 172.404.82.404 deploy
```

Which will set keycloak to listen on IP 172.101.42.101 and GA4GH to listen on IP 172.404.82.404.

### Example 5: Deploy on different ports:

To set keycloak to listen to a different port, use the --keycloak-port option. GA4GH will be automatically configured to communicate with Keycloak using the new port number:

```
python deployer.py -kp 1234 deploy
```

This will cause Keycloak to listen on port 1234 of its IP address.

Similarly, use the --ga4gh-port option to set GA4GH's port number. Keycloak will be configured accordingly:

```
python deployer.py -gp 5678 deploy
```

GA4GH will then listen on port number 5678.

In analogy with setting separate IPs, we may combine these options to set different ports:

```
python deployer.py -kp 7345 -gp 1984 deploy
```

Which will set Keycloak to listen on port 7345 and GA4GH to listen on port 1984.

### Example 6: Test Data Deployment

You can control how much data is preloaded onto the GA4GH server with the --no-data and --extra-data options. By default, a small minimal test data set is loaded onto the server. 

To deploy the GA4GH server with no data:

```
python deployer.py -nd deploy
```

To deploy the GA4GH server with additional data from the 1000 genomes data set:

```
python deployer.py -ed deploy
```

Deploying the additional data will take significantly longer than otherwise.

These options are mutually exclusive.

### Example 7: Funnel Deployment

To deploy a Docker container that holds a Keycloak-authenticated funnel server:

```
python deployer.py -f deploy
```

The funnel server is accessible at port 3002 on the IP 127.0.0.1.

As with Keycloak and GA4GH server, the funnel server can be parameterized in terms of IP and port number:

```
python deployer.py -f -fip 192.168.00.100 -fp 9090 deploy
```

The client application to funnel currently only supports a single test job that repeated prints the date.

### Example 8: Token Tracer Deployment

```
python deployer.py -t deploy
```

This will deploy the token tracer program alongside the Keycloak server.

The token tracer will print alongside the other server debugging statements to stdout as it recieves packets of interest. 

 