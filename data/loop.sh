#!/usr/bin/env bash

for i in {0..19} ; do
     sbatch submit.sh $i
done
