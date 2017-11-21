# Deploys the keycloak server
BootStrap: docker
From: ubuntu:latest

%environment

    DEBIAN_FRONTEND=noninteractive

%setup

    cp /home/vagrant/candig-deploy/keycloak/keycloakStart.sh ${SINGULARITY_ROOTFS}
    cp /home/vagrant/candig-deploy/keycloak/keycloakConfig.json ${SINGULARITY_ROOTFS}
    cp /home/vagrant/candig-deploy/keycloak/keycloakPassword.sh ${SINGULARITY_ROOTFS}

%post

    # Download and install wget, unzip, and java
    apt-get update -y
    apt-get install -y --no-install-recommends apt-utils
    apt-get install -y wget unzip default-jre default-jdk iproute curl libxml2-utils 

    # Go to the srv directory
    cd /srv

    # Download and unzip Keycloak
    wget https://downloads.jboss.org/keycloak/3.3.0.CR2/keycloak-3.3.0.CR2.zip
    unzip keycloak-3.3.0.CR2.zip

    mv /keycloakStart.sh /srv/keycloakStart.sh
    mv /keycloakConfig.json /srv/keycloakConfig.json
    mv /keycloakPassword.sh /srv/keycloakPassword.sh

    chmod +x /srv/keycloakStart.sh
    chmod +x /srv/keycloakPassword.sh

    chmod o+w /srv/keycloak-3.3.0.CR2/standalone
    chmod o+w /srv/keycloak-3.3.0.CR2/standalone/tmp
    chmod o+w /srv/keycloak-3.3.0.CR2/standalone/configuration
    chmod o+rw /srv/keycloak-3.3.0.CR2/standalone/configuration/*

%runscript

    # Start keycloak when the container is run
    # the keycloakStart.sh script determines the local IP on which
    # the keycloak server should listen
    exec /srv/keycloakStart.sh False CanDIG admin admin user user
    