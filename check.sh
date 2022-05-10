#!/usr/bin/env bash

set -x

# EXTERNAL='--span-hosts --wait 2'

wget --spider --recursive --no-directories --no-verbose --level 5 $EXTERNAL http://localhost:1313


