############################################################
## Dockerfile to build the ga4gh server on mod_wsgi-express
## Configurable to use a local dataset
############################################################
FROM ubuntu

# this file is derived from the Dockerfile used to 
# deploy the GA4GH server:

# GA4GH:
# Originally created by Steve Hershman GitHub @hershman
# previously maintained by Alastair Firth, and Maciek Smuga-Otto of the
# UCSC Genomics Institute
# MAINTAINER David Steinberg <david@resium.com>

# This Dockerfile has been modified for the CanDIG project

# Update the sources list
RUN apt-get update  --fix-missing

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
RUN mkdir /srv/ga4gh-server

# copy the source code into the container
COPY ga4gh-server /srv/ga4gh-server

# Configure the python requirements
# Do this as a separate step prior to the build so that changes
# to the GA4GH Server codebase do not trigger a full rebuild of the
# pip requirements.
WORKDIR /srv/ga4gh-server
RUN pip install -r requirements.txt

# install the main code
RUN pip install .

# Write new apache config
RUN cp /srv/ga4gh-server/deploy/001-ga4gh.conf /etc/apache2/sites-available/001-ga4gh.conf
RUN cp /srv/ga4gh-server/deploy/ports.conf /etc/apache2/ports.conf

# Configure apache to serve GA4GH site
WORKDIR /etc/apache2/sites-enabled

RUN a2dissite 000-default
RUN a2ensite 001-ga4gh

# Open port 8000 for apache server on which ga4gh runs
# The port is modified by port-forwarding this container port
EXPOSE 8000

# download and load the compliance data onto the ga4gh server
WORKDIR /srv/ga4gh-server/scripts
RUN python prepare_compliance_data.py -o /srv/ga4gh-compliance-data

# The directory that the user will land in when executing an interactive shell
WORKDIR /srv/ga4gh-server

# Default action: Bring up a webserver instance to run as a daemon
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]


