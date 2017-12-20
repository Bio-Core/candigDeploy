# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Keycloak Deployment Dockerfile
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# Deploys the keycloak server
FROM debian

ENV DEBIAN_FRONTEND="noninteractive"

# Download and install wget, unzip, and java
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y wget unzip default-jre default-jdk iproute curl libxml2-utils 

# Go to the srv directory
WORKDIR /srv

# Download and unzip Keycloak
RUN wget https://downloads.jboss.org/keycloak/3.4.0.Final/keycloak-3.4.0.Final.zip
RUN unzip keycloak-3.4.0.Final.zip

# rename the version-dependent directory name
# to a version-independent name
RUN mv keycloak-3.4.0.Final keycloak

# copy over the configuration files for keycloak into the container
COPY ./keycloakStart.sh /srv/keycloakStart.sh
COPY ../keycloakConfig.json /srv/keycloakConfig.json
COPY ./tokenTracerDeploy.sh /srv/tokenTracerDeploy.sh
COPY ./keycloakPassword.sh /srv/keycloakPassword.sh

RUN chmod a+x /srv/keycloakStart.sh
RUN chmod a+x /srv/tokenTracerDeploy.sh
RUN chmod a+x /srv/keycloakPassword.sh

# install the token tracer
# RUN /srv/tokenTracerDeploy.sh True

# Start keycloak when the container is run
# the keycloakStart.sh script determines the local IP on which
# the keycloak server should listen
CMD /srv/keycloakStart.sh