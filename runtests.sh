#!/bin/bash
for f in $*
do
    heroku local:run python $f
done
