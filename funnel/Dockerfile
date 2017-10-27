

FROM debian

# docker in docker is needed for funnel
# which procures docker containers to run its jobs 
# FROM docker

# add to sources to install docker
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list

# update mirrors
RUN apt-get -y update

# install packages
RUN apt-get install -y wget git build-essential curl docker.io
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash
RUN apt-get install -y nodejs

WORKDIR /home

# get the funnel executable
RUN wget https://github.com/ohsu-comp-bio/funnel/releases/download/0.2.0/funnel-linux-amd64.tar.gz

# unzip the compressed file and clean up
RUN tar -xvf funnel-linux-amd64.tar.gz
RUN rm funnel-linux-amd64.tar.gz

# WORKDIR /home
RUN git clone https://github.com/CanDIG/funnel-node.git 

# copy in the fixes to the source code and the modified configuration files
COPY funnel-node/node-resource/config.json /home/funnel-node/node-resource/config.json
COPY funnel-node/node-resource/funnelAPI.js /home/funnel-node/node-resource/funnelAPI.js

COPY funnel-node/node-client/keycloak.json /home/funnel-node/node-client/keycloak.json
COPY funnel-node/node-client/public/app.js /home/funnel-node/node-client/public/app.js

# copy in the bootstrap script to start the servers
COPY funnelChainStart.sh /home/funnelChainStart.sh
RUN chmod +x /home/funnelChainStart.sh

CMD ["/home/funnelChainStart.sh"]

