#!/bin/bash
declare -a sets=("train" "dev")
path=$1
files_path=$2
labs=$3
key=$4
id=$5

cd "$path"
mkdir sentences
mkdir sentences_sil

for s in "${sets[@]}"
do
  python3 "/home/getalp/zanonbom/xACL/scripts/silence_baseline.py" "$files_path/$s/$key/" "sentences/"
done

python3 "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs" sentences/ sentences_sil/

ls $path/sentences_sil/* > "/home/getalp/zanonbom/eval_acl/silence/$id"
