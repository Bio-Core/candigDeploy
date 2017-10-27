#!/bin/bash

# start the funnel server in the background
/home/funnel-linux-amd64 server & 

# start the node-resource server in background
cd funnel-node/node-resource
npm install --save request nodemon express serve-favicon morgan cookie-parser body-parser jsonwebtoken debug
npm start &
#npm start --prefix /home/funnel-node/node-resource & 

# start the node-client server
cd ../node-client
npm install nodemon body-parser bower connect-busboy connect-flash connect-timeout cookie-parser debug express express-messages express-session express-validator fs-extra jade morgan multer passport passport-local passport-openidconnect request serve-favicon validator keycloak-connect jsonwebtoken --save
cd public
npm install nodemon browserify angular angular-route material-design-lite ng-table node-sass angular-highlightjs angular-markdown-directive --save
./makebundle.sh
cd ..
npm start
#npm start --prefix /home/funnel-node/node-client

exit 0
