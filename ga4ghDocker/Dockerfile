############################################################
## Dockerfile to build the ga4gh server on mod_wsgi-express
## Configurable to use a local dataset
############################################################
FROM ubuntu

# this file is derived from the Dockerfile used to 
# deploy the GA4GH server:

# Originally created by Steve Hershman GitHub @hershman
# previously maintained by Alastair Firth, and Maciek Smuga-Otto of the
# UCSC Genomics Institute
MAINTAINER David Steinberg <david@resium.com>

ARG keycloakIp=127.0.0.1
ARG clientIp=127.0.0.1
ARG clientId="client"
ARG clientSecret="SECRET"
ARG realmName="realm"
# the location of the ga4gh source code to place on the container
ARG sourceDirectory="."       
# if TRUE clone a clean repository from the authentication branch, 
# else use existing source code 
ARG initRepo="FALSE"          
ARG keycloakPort="8080"                    
ARG ga4ghPort="8000"
# the source directory on which the ga4gh code resides
ARG sourceDir="."

ENV keycloakIp=${keycloakIp} clientIp=${clientIp} clientId=${clientId} \ 
clientSecret=${clientSecret} realmName=${realmName} sourceDirectory=${sourceDirectory} \
initRepo=${initRepo} keycloakPort=${keycloakPort} ga4ghPort=${ga4ghPort} sourceDir=${sourceDir}

# Update the sources list

RUN apt-get update  --fix-missing
RUN apt-get upgrade --yes

# Install packages

RUN apt-get install -y tar git curl libcurl4-openssl-dev wget dialog \
    net-tools build-essential python python-dev python-distribute \
    python-pip zlib1g-dev apache2 libapache2-mod-wsgi libxslt1-dev \
    libffi-dev libssl-dev

# Enable wsgi module
RUN a2enmod wsgi

# Create cache directories

RUN mkdir /var/cache/apache2/python-egg-cache && \
    chown www-data:www-data /var/cache/apache2/python-egg-cache/

# build the GA4GH server
RUN mkdir -p /srv/ga4gh
WORKDIR /srv/ga4gh

#RUN git clone https://github.com/CanDIG/ga4gh-server.git
#RUN mv ga4gh-server server

# run the repository initialization script
# the script will pull from the candig auth branch if initRepo is TRUE
# otherwise, the code will be used from sourceDir

./ga4ghInitRepo.sh ${sourceDir} ${initRepo}

# copy the source code into the container
COPY ${sourceDir} /srv/ga4gh
RUN mv ga4gh-server server

WORKDIR /srv/ga4gh/server

# RUN git checkout authentication

# Configure the python requirements
# Do this as a separate step prior to the build so that changes
# to the GA4GH Server codebase do not trigger a full rebuild of the
# pip requirements.

COPY requirements.txt /srv/ga4gh/server/

RUN pip install -r requirements.txt

# copy in the modified candig files

#COPY frontend.py /srv/ga4gh/server/ga4gh/server/frontend.py
#COPY serverconfig.py /srv/ga4gh/server/ga4gh/server/serverconfig.py

COPY ./ga4ghConfig.py ./ga4ghConfig.py
RUN chmod +x ga4ghConfig.py

# install the code

RUN pip install .

# Write new apache config

RUN cp /srv/ga4gh/server/deploy/001-ga4gh.conf \
/etc/apache2/sites-available/001-ga4gh.conf

# this deployment is NOT efficient, there are some source files that are not
# used in deployment still lingering for example, /deploy, /docs

# Write application.wsgi

RUN cp /srv/ga4gh/server/deploy/application.wsgi /srv/ga4gh/application.wsgi
RUN cp /srv/ga4gh/server/deploy/config.py /srv/ga4gh/config.py

# Configure apache to serve GA4GH site

WORKDIR /etc/apache2/sites-enabled

RUN a2dissite 000-default
RUN a2ensite 001-ga4gh

# Open port 80 for HTTP (apache server on which ga4gh runs)
EXPOSE 80

# Prepare container for deployment
# The directory that the user will land in when executing an interactive shell

WORKDIR /srv/ga4gh/server

# download and load the compliance data onto the ga4gh server

RUN python scripts/prepare_compliance_data.py -o ../ga4gh-compliance-data

# run the client_secrets configuration script

RUN python ./ga4ghConfig.py client_secrets.json ${keycloakIp} ${clientId} \
${clientSecret} ${clientIp} ${realmName} ${keycloakPort} ${ga4ghPort}

# eliminate the deployment files that are unnecessary for server operations

RUN rm -r /srv/ga4gh/server/docs
RUN rm -r /srv/ga4gh/server/deploy
RUN rm -r /srv/ga4gh/server/tests
RUN rm -r /srv/ga4gh/server/tools

# there are more still to remove

# Default action: Bring up a webserver instance to run as a daemon

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]


