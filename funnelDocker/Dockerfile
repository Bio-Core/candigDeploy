FROM debian

# update mirrors
RUN apt-get update

# install packages
RUN apt-get install -y wget git npm

WRKDIR /home

# get the funnel executable
RUN wget https://github.com/ohsu-comp-bio/funnel/releases/download/0.2.0/funnel-linux-amd64.tar.gz

# unzip the compressed file
RUN tar -xvf funnel-linux-amd64.tar.gz
RUN rm funnel-linux-amd64.tar.gz

# WRKDIR /home/funnel

# start the funnel server locally
# RUN ./funnel-linux-amd64 server

WRKDIR /home

RUN git clone https://github.com/CanDIG/funnel-node.git 

COPY node-resource/config.json /home/funnel-node/node-resource/config.json
COPY node-resource/funnelAPI.js /home/funnel-node/node-resource/funnelAPI.js

WRKDIR /home/funnel-node/node-resource 
RUN npm install

# RUN npm start

COPY node-client/keycloak.json /home/funnel-node/node-client/keycloak.json
COPY node-client/public/app.js /home/funnel-node/node-client/public/app.js

WRKDIR /home/funnel-node/node-client
npm install

WRKDIR /home/funnel-node/node-client/public

npm install

RUN ./makebundle.sh

WRKDIR /home

COPY funnelChainStart.sh /home/funnelChainStart.sh

CMD ['/home/funnelChainStart.sh']