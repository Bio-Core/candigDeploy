#!/bin/bash

tokenTracer=${1}

if [ ${tokenTracer} == "True" ]
then
    apt-get install -y python python-pip git tshark
    git clone https://github.com/Bio-Core/tokenTracer.git
    pip install pyshark
fi

exit 0
