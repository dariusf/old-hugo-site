#!/usr/bin/env bash

set -x

# fast local check
wget --spider --recursive --no-directories \
  --no-verbose --level 5 $EXTERNAL \
  http://localhost:1313 2>&1 \
  | grep -v 'unlink: No such file or directory' \
  | grep -v 'failed: Connection refused.'

# remote check
# --wait 2

# wget --spider --recursive --no-directories \
#   --level 1 --span-hosts --timeout 8 --tries 1 \
#   http://localhost:1313 2>&1
