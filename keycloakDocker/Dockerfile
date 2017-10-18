# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# Keycloak Deployment Dockerfile
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# Deploys the keycloak server

FROM debian

#choose the password and username of the admin account
#choose the realm name and the client_id to establish

ARG adminUsername="admin"
ARG adminPassword="admin"
ARG realmName="realm"
ARG clientId="client"
ARG ga4ghIp="127.0.0.1"
ARG userUsername="user"
ARG userPassword="user"
ARG ga4ghPort="8000"

ENV adminUsername=${adminUsername} adminPassword=${adminPassword} \
realmName=${realmName} clientId=${clientId} ga4ghIp=${ga4ghIp} \
userUsername=${userUsername} userPassword=${userPassword} \
ga4ghPort=${ga4ghPort}

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

COPY ./keycloakAdmin.sh /home/keycloakAdmin.sh
COPY ./keycloakStart.sh /home/keycloakStart.sh
COPY ./keycloakConfig.json /home/keycloakConfig.json

RUN chmod +x /home/keycloakAdmin.sh
RUN chmod +x /home/keycloakStart.sh

RUN /home/keycloakAdmin.sh ${adminUsername} ${adminPassword} ${realmName} \
${clientId} ${ga4ghIp} ${userUsername} ${userPassword} ${ga4ghPort}

# Start keycloak when the container is run

# the keycloakStart.sh script determines the local IP on which
# the keycloak server should listen

CMD ["/home/keycloakStart.sh"]







