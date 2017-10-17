#!/bin/bash

# initializes a new repository with the ga4gh code from the authentication branch
# this code will be used in the deployment of the docker container

# read command line args

SOURCE_DIR=${1} 

# save the current directory location
ORIG_DIR=$(pwd)

# go to the source code directory
cd ${SOURCE_DIR}

# clone in the authentication candig branch
git clone https://github.com/CanDIG/ga4gh-server.git
cd ga4gh-server
git checkout authentication   

# copy in the modified candig files 
cp ${ORIG_DIR}/ga4gh-server/frontend.py ${SOURCE_DIR}/ga4gh-server/ga4gh/server/frontend.py
cp ${ORIG_DIR}/ga4gh-server/serverconfig.py ${SOURCE_DIR}/ga4gh-server/ga4gh/server/serverconfig.py

#COPY code   

# change back to the original directory
#cd ${ORIG_DIR}

exit 0 
