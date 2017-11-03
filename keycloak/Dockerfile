# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Keycloak Deployment Dockerfile
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# Deploys the keycloak server
FROM debian

ARG tokenTracer="False"

ARG realmName="CanDIG"

ARG adminUsername="admin"
ARG adminPassword="admin"
ARG userUsername="user"
ARG userPassword="user"

ENV tokenTracer=$tokenTracer

ENV realmName=$realmName

ENV adminUsername=$adminUsername
ENV adminPassword=$adminPassword
ENV userUsername=$userUsername
ENV userPassword=$userPassword

ENV DEBIAN_FRONTEND="noninteractive"

# Download and install wget, unzip, and java
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y wget unzip default-jre default-jdk iproute curl libxml2-utils 

# Go to the srv directory
WORKDIR /srv

# Download and unzip Keycloak
RUN wget https://downloads.jboss.org/keycloak/3.3.0.CR2/keycloak-3.3.0.CR2.zip
RUN unzip keycloak-3.3.0.CR2.zip

# copy over the configuration files for keycloak into the container
COPY ./keycloakStart.sh /srv/keycloakStart.sh
COPY ./keycloakConfig.json /srv/keycloakConfig.json
COPY ./tokenTracerDeploy.sh /srv/tokenTracerDeploy.sh
COPY ./keycloakPassword.sh /srv/keycloakPassword.sh

RUN chmod +x /srv/keycloakStart.sh
RUN chmod +x /srv/tokenTracerDeploy.sh
RUN chmod +x /srv/keycloakPassword.sh

RUN /srv/tokenTracerDeploy.sh $tokenTracer

# Start keycloak when the container is run
# the keycloakStart.sh script determines the local IP on which
# the keycloak server should listen
CMD /srv/keycloakStart.sh $tokenTracer $realmName $adminUsername $adminPassword $userUsername $userPassword







