#!/bin/sh
export PYTHONPATH=${PYTHONPATH}:.:..
#echo $PYTHONPATH
if [ -d bin ]; then
	bin/pyxis
else
	../bin/pyxis
fi

