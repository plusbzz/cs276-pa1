#!/bin/bash
SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
python $SCRIPTPATH/query.py $1
