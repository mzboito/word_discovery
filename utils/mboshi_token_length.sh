#!/bin/bash

root=$1

/home/getalp/zanonbom/xACL/scripts/mboshi_seg_fetcher.sh $root > "/home/getalp/zanonbom/eval_acl/token_length/$2_temp"
python3 "/home/getalp/zanonbom/average_tokens.py" "/home/getalp/zanonbom/eval_acl/token_length/$2_temp" "/home/getalp/zanonbom/eval_acl/token_length/$2"
#rm "/home/getalp/zanonbom/eval_acl/token_length/$2_temp"
