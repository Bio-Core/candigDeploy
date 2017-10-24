#!/bin/bash

# start the funnel server in the background
/home/funnel/funnel-linux-amd64 server & 

# start the node-resource server in background
npm start /home/funnel-node/node-resource & 

# start the node-client server
npm start /home/funnel-node/node-client

exit 0
