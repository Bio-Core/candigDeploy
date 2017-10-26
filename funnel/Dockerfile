FROM debian

# update mirrors
RUN apt-get -y update

# install packages
RUN apt-get install -y wget git build-essential curl
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash
RUN apt-get install -y nodejs


WORKDIR /home

# get the funnel executable
RUN wget https://github.com/ohsu-comp-bio/funnel/releases/download/0.2.0/funnel-linux-amd64.tar.gz

# unzip the compressed file
RUN tar -xvf funnel-linux-amd64.tar.gz
RUN rm funnel-linux-amd64.tar.gz

# start the funnel server locally
# RUN ./funnel-linux-amd64 server

WORKDIR /home
RUN git clone https://github.com/CanDIG/funnel-node.git 

COPY funnel-node/node-resource/config.json /home/funnel-node/node-resource/config.json
COPY funnel-node/node-resource/funnelAPI.js /home/funnel-node/node-resource/funnelAPI.js

WORKDIR /home/funnel-node/node-resource 
RUN npm install

COPY funnel-node/node-client/keycloak.json /home/funnel-node/node-client/keycloak.json
COPY funnel-node/node-client/public/app.js /home/funnel-node/node-client/public/app.js

WORKDIR /home/funnel-node/node-client
RUN npm install

WORKDIR /home/funnel-node/node-client/public
RUN npm install
RUN ./makebundle.sh

WORKDIR /home
COPY funnelChainStart.sh /home/funnelChainStart.sh
RUN chmod +x /home/funnelChainStart.sh

CMD ["/home/funnelChainStart.sh"]

