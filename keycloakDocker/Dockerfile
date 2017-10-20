# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Keycloak Deployment Dockerfile
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# Deploys the keycloak server
FROM debian

ENV DEBIAN_FRONTEND noninteractive

# Download and install wget, unzip, and java
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y wget unzip default-jre default-jdk iproute curl libxml2-utils 

# Go to the home directory
WORKDIR /home

# Download and unzip Keycloak
RUN wget https://downloads.jboss.org/keycloak/3.3.0.CR2/keycloak-3.3.0.CR2.zip
RUN unzip keycloak-3.3.0.CR2.zip

WORKDIR /home

# copy over the configuration files for keycloak into the container
COPY ./keycloakStart.sh /home/keycloakStart.sh
COPY ./keycloakConfig.json /home/keycloakConfig.json

RUN chmod +x /home/keycloakStart.sh

# Start keycloak when the container is run
# the keycloakStart.sh script determines the local IP on which
# the keycloak server should listen
CMD ["/home/keycloakStart.sh"]







