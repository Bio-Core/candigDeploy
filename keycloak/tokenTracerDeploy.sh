#!/bin/bash

tokenTracer=${1}

echo "Token tracer deployment.sh"
echo ${tokenTracer}

if [ ${tokenTracer} == "True" ]
then
    apt-get install -y python python-pip git tshark
    git clone https://github.com/Bio-Core/tokenTracer.git
    pip install pyshark
fi

exit 0
