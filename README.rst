=====================================================
CanDIG Deployment Package
=====================================================

1.1 Overview:
-------------------

This script deploys application servers for the CanDIG project:

1. Keycloak authentication server 
2. Authentication branch CanDIG GA4GH application server

The deployment can be faciliated either through Docker, Singularity, or Vagrant.

The servers are configured to be registered with one another and communicate with such that a user must authenticate with the GA4GH server through a login page using the username and password specified prior to using its REST API.

In each deployment, the Keycloak server is essential, as it provides login and authentication facilities for each application server that is available to the deployment program.

The deployer also supports:

- The loading of test data onto the GA4GH server
- Execution of a token tracer debugging program
- Deployment of a Keycloak-authenticated Funnel application server

The source code can be found at:

https://github.com/Bio-Core/candigDeploy


1.2 Requirements:
---------------------

- Linux OR MacOS
- Docker OR Vagrant OR Singularity
- git
- Python 2.7+
- pip
- PyYAML
- gunzip (for Singularity)

Singularity cannot be used on a MacOS. Use either VirtualBox with a guest Linux operating system or the Vagrant deployment option to deploy via singularity in this case.

Docker or Vagrant may need a hypervisor such as VirtualBox in order to work.

This script requires root permissions for Docker and Vagrant deployment options. 
For non-root use, follow the non-root installation instructions and use a Singularity deployment.

1.3 Installation
--------------------

1.3.1 Pip Installation (non-root)
====================================

It is recommended for end-users to install the script via pip as follows:

1. Clone the git repository:

::

    $ git clone https://github.com/Bio-Core/candigDeploy.git

2. Change directory into the top level of the repository:

::

    $ cd candigDeploy

3. For a non-root installation, use:

::

    $ pip install --user .

4. For Linux (Debian) users, add ``~/.local/bin`` to the PATH. For Mac OS users, add ``~/Library/Python/2.7/bin`` to the PATH. This directory contains the installed executable:

::

   $ PATH=$PATH:~/.local/bin
   $ export PATH

This will make the command available in your current terminal. You can verify that it works with the command:

::

    $ candigDeploy -h

A help menu should appear.


5. You can add this command anywhere in your ``~/.bash_profile`` to make the command available whenever you open a new terminal.
You may have to create this file if it does not exist.


1.3.2 Pip Installation (root)
===================================

Installing the script as root will allow the script to be run as any user.
However, users will require root privileges to execute the script. 
Root must also have the dependencies installed system-wide.

1. Clone the git repository:

::

    $ git clone https://github.com/Bio-Core/candigDeploy.git

2. Change directory into the top level of the repository:

::

    $ cd candigDeploy

3. Pip-install locally from the top-level directory:

::

    $ pip install .

This will perform a full-system install of the deployer.

The deployer should now be installed as a command-line utility called candigDeploy.


1.3.3 Uninstallation
=================================

To uninstall from the system, use pip:

::

    $ pip uninstall candigDeploy


1.3.4 Running the module directly
===================================

The module can be run directly through Python. 
From the top-level directory of the repository we may call the deployer:

::

   $ python deployer/deployer.py

Or alternatively, the script may be called without invoking python directly:

::

   $ ./deployer/deployer.py


1.4 Command-Line Arguments:
------------------------------

The command-line program is able to take in arguments for deployment. 
The details of such command-line arguments can be viewed using 
the ``-h`` or ``--help`` option:

::

    $ candigDeploy --help

The command-line options can modify the following variables:

+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| Argument (Long Form)    | Short Form | Default                       | Description                                                                                        | 
+=========================+============+===============================+====================================================================================================+
| ip                      | i          | None                          | The IP to assign all servers to listen on. Overrides all other IP settings.                        |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| keycloak-ip             | kip        | 127.0.0.1                     | The IP of the Keycloak server to listen on.                                                        |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+ 
| ga4gh-ip                | gip        | 127.0.0.1                     | The IP of the GA4GH server to listen on.                                                           |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+ 
| keycloak-port           | kp         | 8080                          | The port number the Keycloak server listens on.                                                    |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| ga4gh-port              | gp         | 8000                          | The port number of the Ga4gh server listens on.                                                    |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| ga4gh-id                | gid        | ga4gh                         | The Keycloak client id of the GA4GH server with which it will register with Keycloak as a client   |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+ 
| realm-name              | r          | CanDIG                        | The name of the Keycloak realm on which the GA4GH server registers as a client                     |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+ 
| keycloak-image-name     | kin        | keycloak_candig               | The name to assign the resulting Docker image of the Keycloak server                               |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| keycloak-container-name | kcn        | keycloak_candig               | The name to assign the container running the Keycloak server image                                 |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| ga4gh-image-name        | gin        | ga4gh_candig                  | The name to assign the resulting Docker image of the GA4GH server                                  |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| ga4gh-container-name    | gcn        | ga4gh_candig                  | The name to assign the container running the GA4GH server image                                    |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| admin-username          | au         | admin                         | The username of the Keycloak administrator account                                                 |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| user-username           | uu         | user                          | The username of the user to login to the GA4GH server at the login page                            |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+   
| override                | o          | False                         | Overrides the target source directory for ga4gh  with a clean repository pulled from github        |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| singularity             | s          | False                         | Deploys GA4GH and Keycloak servers on Singularity                                                  |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| token-tracer            | t          | False                         | Deploys the token tracer on the Keycloak server container (Docker only)                            |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel                  | f          | False                         | Deploys the funnel server in addition to GA4GH and keycloak (Docker only)                          |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| no-data                 | nd         | False                         | Deploys the GA4GH server with no data loaded (Docker only)                                         |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| extra-data              | ed         | False                         | Deploys the GA4GH server with additional 1000g data (Docker only)                                  |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| ga4gh-secret            | cs         | SEE CONFIGURATION             | The client secret for the GA4GH server                                                             |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-ip               | fip        | 127.0.0.1                     | The IP on which the funnel server is located                                                       |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-port             | fp         | 3002                          | The port number on which funnel listens                                                            |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-id               | fid        | funnel                        | The funnel client id for registration with Keycloak                                                |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-container-name   | fcn        | funnel_candig                 | The container name of the funnel Docker container                                                  |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-image-name       | fin        | funnel_candig                 | The tag of the funnel Docker image name                                                            |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| funnel-secret           | fs         | SEE CONFIGURATION             | The client secret for the funnel server                                                            |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| vagrant                 | v          | False                         | Deploys a Vagrant container linked to the deployer on which Singularity containers may be deployed |
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+
| vagrant-ip              | vip        | 127.0.0.1                     | The IP address of the Vagrant container                                                            | 
+-------------------------+------------+-------------------------------+----------------------------------------------------------------------------------------------------+

As by convention, long form arguments are given with the double hyphen prefix "--" and short form arguments are given a single hyphen "-", as seen in the examples. 

1.5 Server Access and Login:
-------------------------------

The GA4GH server can be accessed at ``ga4gh-ip:ga4gh-port`` (default: ``127.0.0.1:8000``)
and the Keycloak server can be accessed at ``keycloak-ip:keycloak-port`` (default: ``127.0.0.1:8080``).

On the master realm on the administration console for Keycloak, the administration account can be accessed with the defaults:

- username: admin
- password: admin

On the realmName realm (default: CanDIG), the user account can be accessed with the defaults:

- username: user
- password: user

Note the interface on which the software containers may be accessed. You may list the interfaces using a tool such as ``ip`` (with ``ip addr``) or ``ifconfig``.
If the software containers are running with a software hypervisor, such as VirtualBox, you may have to listen on the interface dedicated 
to the virtual machine operating system, such as ``vboxnet0``, instead of listening locally on loopback with localhost. 

For instance, if you are running Docker using docker-machine with a software-based VirtualBox hypervisor, you can determine the IP address on which to set the deployment script using ``ip addr``:

::

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


You would then set the deployer to configure GA4GH and Keycloak to listen on 192.168.12.1, the IP address found in the inet field for the vboxnet0 interface:

::

    $ candigDeploy -i 192.168.12.1

The deployer program will create a source code directory for GA4GH if one does not exist. It will reuse this source code in subsequent deployments, and reconfigure it based on the options provided. 

1.5.1 Private IP Addresses
============================

When deploying through VirtualBox or any software hypervisor, the ip addresses assigned as an interface must be within the private range of IP addresses. This is particularly relevant for Vagrant deployment if used with VirtualBox, where the vagrant IP address must be private. 

The private IP address range is as follows:

- ``192.168.0.0`` - ``192.168.255.255``
- ``172.16.0.0`` - ``172.31.255.255``
- ``10.0.0.0`` - ``10.255.255.255``

1.6 Examples
-----------------

1.6.1 Example 1: Keycloak and GA4GH Server Docker Deployment
===============================================================

To deploy Keycloak and GA4GH on separate Docker containers on localhost, invoke the script with no arguments:

::

    $ candigDeploy


1.6.2 Example 2: Keycloak and GA4GH Server Singularity Deployment
=============================================================================

To deploy Keycloak and GA4GH on separate Singularity containers, use the ``--singularity`` option:

::

    $ candigDeploy -s

Both servers will have the IP address ``127.0.0.1`` accessible on the loopback network interface with the default ports. 

The ``--singularity`` option is designed to specifically work without root privileges in Linux environments
and will download pre-built and pre-configured images for both Keycloak and GA4GH. 

To terminate the servers, kill their outstanding processes with ``kill PID`` where ``PID`` is the process id.
For Keycloak, the process id can be found using ``ps -e | egrep java`` or ``ps -e | egrep standalone``. 
For GA4GH, the process id can be found using ``ps -e | egrep python`` or ``ps -e | egrep ga4gh_server``.

You can verify whether the servers have terminated through curl with ``curl 127.0.0.1:8000`` or ``curl 127.0.0.1:8080``.

With the Singularity deployment, you may change the IP and port with the ``--ip``, ``--keycloak-port``, and ``--ga4gh-port`` options respectively.
However, the Singularity deployment does not currently work with ``--realm-name``, ``--user-username``, ``--user-password``, ``--admin-username``, and ``--admin-password``.

1.6.3 Example 3: Deployment on a different IP address
===========================================================

To deploy Keycloak and GA4GH server with a different IP address use the ``--ip`` option. This will change both the Keycloak and GA4GH server IPs to the IP given:

::

    $ candigDeploy -i 192.168.12.123

This will cause both servers to be configured on the IP address ``192.168.12.123``. 

You can also change the IP addresses of Keycloak and GA4GH separately through the ``--keycloak-ip`` and ``--ga4gh-ip`` options. This allows the servers to listen on different IP addresses. These will be overrided by the ``--ip`` option if it is used.

::

    $ candigDeploy -kip 127.123.45.678

This causes Keycloak to be assigned the IP address ``127.123.45.678``. GA4GH will still listen on the default ``127.0.0.1``. 

For GA4GH, we can assign an IP ``192.168.00.100``:

::

    $ candigDeploy -gip 192.168.00.100

Keycloak will then listen to the default ``127.0.0.1`` address.

We can also combine these arguments:

::

    $ candigDeploy -kip 172.101.42.101 -gip 172.404.82.404

Which will set keycloak to listen on IP ``172.101.42.101`` and GA4GH to listen on IP ``172.404.82.404``.

1.6.4 Example 4: Deploy on different ports:
===========================================================

To set Keycloak to listen to a different port, use the ``--keycloak-port`` option. GA4GH will be automatically configured to communicate with Keycloak using the new port number:

::

    $ candigDeploy -kp 1234

This will cause Keycloak to listen on port ``1234`` of its IP address.

Similarly, use the ``--ga4gh-port`` option to set GA4GH's port number. Keycloak will be configured accordingly:

::

    $ candigDeploy -gp 5678

GA4GH will then listen on port number ``5678``.

In analogy with setting separate IPs, we may combine these options to set different ports:

::

    $ candigDeploy -kp 7345 -gp 1984

Which will set Keycloak to listen on port ``7345`` and GA4GH to listen on port ``1984``.


1.6.5 Example 5: Reverting the Source Configuration
===========================================================

To revert the GA4GH source to its original version, (found in ``deployer/ga4gh/ga4gh-server`` by default), use the ``--override`` option in the deployment. 
This will overwrite an existing changes that you have made to development.
This is largerly used for testing purposes to test installations from scratch.
End-users typically will not need to use this option.

::

    $ candigDeploy -o


1.6.6 Example 6: Test Data Deployment
===========================================================

You can control how much data is preloaded onto the GA4GH server with the ``--no-data`` and ``--extra-data`` options. By default, a small minimal test data set is loaded onto the server. 

To deploy the GA4GH server with no data:

::

    candigDeploy -nd deploy

To deploy the GA4GH server with additional data from the 1000 Genomes data set:

::

    $ candigDeploy -ed

Deploying the additional data will take significantly longer than otherwise.

These options are mutually exclusive.

1.6.7 Example 7: Funnel Deployment
===========================================================

To deploy a Docker container that holds a Keycloak-authenticated funnel server:

::

    $ candigDeploy -f

The funnel server is accessible at port ``3002`` on the IP ``127.0.0.1``.

As with Keycloak and GA4GH server, the funnel server can be parameterized in terms of IP and port number:

::

    $ candigDeploy -f -fip 192.168.00.100 -fp 9090 

The client application to funnel currently only supports a single test job that repeated prints the date.

1.6.8. Example 8: Token Tracer Deployment
===========================================================

::

    $ candigDeploy -t

This will deploy the token tracer program alongside the Keycloak server.

The token tracer will print alongside the other server debugging statements to stdout as it recieves packets of interest. 

 
1.6.9 Example 9: Vagrant Deployment
===========================================================

The GA4GH and Keycloak servers may be deployed via Vagrant. This deployment assumes root-level privileges to work.

::

    $ candigDeploy -v -vip 192.168.99.100

This will deploy the servers with the IP configured to ``192.168.99.100`` on default ports for both servers.
Other command-line options are not supported with Vagrant deployment.

If the Vagrant containers fail to be removed, delete processes associated with Vagrant using ``ps -e`` and ``kill PID``. 
You should look for processes under VBox, VBoxHeadless, ruby, or vagrant and delete those. 

::

    $ ps -e | egrep VBox
    $ ps -e | egrep ruby 
    $ ps -e | egrep vagrant
