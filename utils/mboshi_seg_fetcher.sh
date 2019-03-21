#!/bin/bash
declare -a key=("1" "2" "3" "4" "5")
root=$1

for k in "${key[@]}"
do
  for m in $root$k/*.segmented.clean.encoded
  do
    #echo $m
    python3 "/home/getalp/zanonbom/avg_token_length.py" "$m" #> "/home/getalp/zanonbom/eval_acl/token_length/$2_temp"
    #python3 "/home/getalp/zanonbom/average_tokens.py" "/home/getalp/zanonbom/eval_acl/token_length/$2_temp" "/home/getalp/zanonbom/eval_acl/token_length/$2"
    #rm "/home/getalp/zanonbom/eval_acl/token_length/$2_temp"
  done
done
