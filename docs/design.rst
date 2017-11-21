=================================
CanDIG Deployer Design
=================================

1.0 Design Description
=========================


1.1 Directory Structure
--------------------------




1.2 Class Structure
--------------------------



2.0 Testing
=================

2.1 Manual Testing
-----------------------

To manually test, examine the following schemes:


2.1.1 Base Deployment
-------------------------

- Run the deployer using docker for only Keycloak and GA4GH

``python deployer.py -i 192.168.12.123 deploy``

Where 192.168.12.123 is a valid network interface. 

The test is successful if one can obtain the webpage of GA4GH by logging in through:

``http://192.168.12.123:8000``

and if the user can log into Keycloak's master realm as the administrator on:

``http://192.168.12.123:8080``

The base deployment should be done both without a GA4GH server source directory and with one to test the effects of caching in Docker.

One can test building from scratch using the ``--override`` option:

``python deployer.py -i 192.168.12.123 -o deploy``


2.1.2 Vagrant Deployment
-----------------------------

This setup tests both the Vagrant deployment and Singularity

``python deployer.py -v -vip 192.168.12.123 deploy``

This should satisfy the requirements of the  base deployment.

2.1.3 Funnel Deployment
------------------------------

``python deployer.py -i	192.168.12.123 -f deploy``

One should satisfy the requirements of the base deployment and be able to access:

``http://192.168.12.123:3003``

and submit a job successfully to funnel. An alpine container should appear in docker that is running the job.

2.1.4 Server Configuration Testing
----------------------------------------

Test non-standard ports, usernames, and passwords to check that the Keycloak configuration with GA4GH is working:

``python deployer.py -i 192.168.12.123 -gip 9000 -kip 9090 -un jdoe -up jdoe -au jdoe -ap jdoe deploy``

The servers should behave as usual but instead use the following credentials on both:

- Username: jdoe
- Password: jdoe

The Keycloak server will then be accessible at ``192.168.12.123:9090`` and the GA4GH server will be accessible at ``192.168.12.123:9000``.

2.1.5 Token Tracer Deployment
----------------------------------

The token tracer may be tested with the --token-tracer option in standard deployment:

``python deployer.py -i 192.168.12.123 -t deploy``

Once the deployment is complete, logging into the GA4GH server should 
cause packet information to be printed that shows the exchange of user authentication tokens.