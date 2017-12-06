Deployment Software Containers
=================================

There are five types of containers used in the deployment scheme:

1. GA4GH Docker Container
2. Keycloak Docker Container
3. GA4GH Singularity Container
4. Keycloak Singularity Container
5. Deployer Vagrant Container

Manual Acquisition and Construction
-------------------------------------

The GA4GH and Singularity Docker containers can be built using 
their respective Dockerfiles found in ``deployer/ga4gh/Dockerfile`` and
``deployer/keycloak/Dockerfile``.

The GA4GH Singularity container may be pulled from
Singularity Hub using Singularity:

``singularity pull shub://DaleDupont/Singularity-GA4GH``

The Keycloak Singularity container must be downloaded from the release
on its dedicated GitHub Repository:

``https://github.com/DaleDupont/Singularity-Keycloak/releases/0.0.1.git``

This container cannot be built using standard methods nor uploaded
to Singulartiy Hub. It must be built and run as a ``--writable`` image.

The Vagrant container may be built using the Vagrantfile found
in the ``vagrant`` directory of the deployer: ``deployer/vagrant/Vagrantfile``.
