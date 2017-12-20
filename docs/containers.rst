Deployment Software Containers
=================================

There are five types of containers used in the deployment scheme:

1. GA4GH Docker Container
2. Keycloak Docker Container
3. GA4GH Singularity Container
4. Keycloak Singularity Container
5. Deployer Vagrant Container

1.0 Manual Acquisition and Construction
-------------------------------------

1.1 Docker Containers
~~~~~~~~~~~~~~~~~~~~~~~~

The GA4GH and Singularity Docker container images can be built using 
their respective Dockerfiles found in ``deployer/ga4gh/Dockerfile`` and
``deployer/keycloak/Dockerfile``.


The GA4GH image is pulled directly from Docker Hub.
You may built your own GA4GH image using the Dockerfile,
upload it to Docker Hub, and redirect the Deployer
to pull from that repository by changing the imageRepo
variable in the ``ga4gh.py`` module. The current deployer pulls
from:

:: 

    https://hub.docker.com/r/dalos/docker-ga4gh/


1.2 Singularity Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The GA4GH Singularity container may be pulled from
Singularity Hub using Singularity:

::

    singularity pull shub://DaleDupont/Singularity-GA4GH

The Keycloak Singularity container must be downloaded from the release
on its dedicated GitHub Repository:

::

    https://github.com/DaleDupont/Singularity-Keycloak/releases/0.0.1.git

This container cannot be built using standard methods nor uploaded
to Singulartiy Hub. It must be built and run as a ``--writable`` image.

1.3 Vagrant Container
~~~~~~~~~~~~~~~~~~~~~~~~

The Vagrant container may be built using the Vagrantfile found
in the ``vagrant`` directory of the deployer: ``deployer/vagrant/Vagrantfile``.
