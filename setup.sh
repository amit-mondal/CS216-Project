#!/bin/bash
set -e

# Clone the p4 tutorial repo
git clone https://github.com/p4lang/tutorials.git
cd tutorials

# Copy the calc directory, since that's what we've based this on
mv exercises/calc .

# Remove all the other exercises, since we don't need them
rm -rf exercises/*

mv calc exercises/tcam
cp ../*.py exercises/tcam
cd exercises/tcam
