=================================
CanDIG Deployer Design
=================================

1.0 Design Description
=========================


1.1 Directory Structure
--------------------------

The structure of the deployer is expressed through its directory structure.
The source code is housed in the deployer subdirectory. 

Within the deployer subdirectory is the primary Python module, deployer.py.
This contains the deployer singleton and serves as the entrypoint to the Python script.

A supporting module is the cmdparse.py Python module. This script holds the 
cmdparse class that supports command-line options. From this module,
the possible command-line options that can be read are configured here 
through its parser.

There are several subdirectories, each containing a specific application server or
deployment scheme that has been specified for the deployer.

There are three distinct applications:

1. GA4GH Server
2. Keycloak Server
3. Funnel Server

Each of these uses authentication faciliated by Keycloak.
Therefore, in order for authentication to work, it is required 
at at least Keycloak be deployed.

The Funnel and Ga4GH servers are independent of each other.

Each of these also has several deployment schemes:

1. Docker
2. Singularity
3. Vagrant

Vagrant is largely used to faciliate testing of root-access 
singularity deployments on MacOS systems.

1.2 Class Structure
--------------------------



1.3 Keycloak Configuration
-----------------------------

Keycloak is automatically configured with a series 
of default parameters that enable it to communicate
with the GA4GH and Funnel application servers.

Part of this configuration can be modified through the
use of the command-line arguments.

These command-line arguments are used to modify 
some of the existing configuration that has 
significance for the end-users. Some of these 
apply to all application servers, including Keycloak,
while others may exclude or only include Keycloak.

1. IP Addresses
2. Port Numbers
3. Realm Names
4. User name and password
5. Admin name and password

Further configuration must be made either by
directly modifying the keycloakConfig.json file
or by interfacing with the administration console.

2.0 Testing
=================

2.1 Manual Testing
-----------------------

To manually test, examine the following schemes:

2.1.1 Base Deployment
-------------------------

- Run the deployer using docker for only Keycloak and GA4GH

::

    $ python deployer.py -i 192.168.12.12

Where 192.168.12.123 is a valid network interface. 

The test is successful if one can obtain the webpage of GA4GH by logging in through:

::

    http://192.168.12.123:8000

and if the user can log into Keycloak's master realm as the administrator on:

::

    http://192.168.12.123:8080

The base deployment should be done both without a GA4GH server source directory and with one to test the effects of caching in Docker.

One can test building from scratch using the ``--override`` option:

::

    $ python deployer.py -i 192.168.12.123 -o


2.1.2 Vagrant Deployment
-----------------------------

This setup tests both the Vagrant deployment and Singularity

::

    $ python deployer.py -v -vip 192.168.12.123

This should satisfy the requirements of the  base deployment.

2.1.3 Funnel Deployment
------------------------------

::

    $ python deployer.py -i 192.168.12.123 -f

One should satisfy the requirements of the base deployment and be able to access:

::

    http://192.168.12.123:3003

and submit a job successfully to funnel. An alpine container should appear in docker that is running the job.

2.1.4 Server Configuration Testing
----------------------------------------

Test non-standard ports, usernames, and passwords to check that the Keycloak configuration with GA4GH is working:

::

    $ python deployer.py -i 192.168.12.123 -gip 9000 -kip 9090 -un jdoe -up jdoe -au jdoe -ap jdoe

The servers should behave as usual but instead use the following credentials on both:

- Username: ``jdoe``
- Password: ``jdoe``

The Keycloak server will then be accessible at ``192.168.12.123:9090`` and the GA4GH server will be accessible at ``192.168.12.123:9000``.

2.1.5 Token Tracer Deployment
----------------------------------

The token tracer may be tested with the ``--token-tracer`` option in standard deployment:

::

    $ python deployer.py -i 192.168.12.123 -t

Once the deployment is complete, logging into the GA4GH server should 
cause packet information to be printed that shows the exchange of user authentication tokens.
