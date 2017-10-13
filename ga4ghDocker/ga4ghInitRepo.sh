#!/bin/bash

# read command line args

sourceDir = ${1} 
initRepo = ${2}

if [ initRepo == 'TRUE' ]; then
   # save the current directory location
   ORIG_DIR=$(pwd)

   # go to the source code directory
   cd ${SOURCE_DIR}
   
   # clone in the authentication candig branch
   git clone https://github.com/CanDIG/ga4gh-server.git
   cd ga4gh-server
   git checkout authentication   

   # copy in the modified candig files 
   cp ${ORIG_DIR}/frontend.py ${SOURCE_DIR}/ga4gh/server/frontend.py
   cp ${ORG_DIR}/serverconfig.py ${SOURCE_DIR}/ga4gh/server/serverconfig.py

   COPY code   

   # change back to the original directory
   cd ${ORIG_DIR}
fi

exit 0 
