#!/bin/bash

root=$1
labs=$2
ids_file=$3
id=$4

cd "$root"

mkdir avg_attention_matrices
mkdir avg_sentences
mkdir avg_sentences_sil

python3 "/home/getalp/zanonbom/word_discovery/post_processing/intramodel_merge_matrices.py" "--transformer" "--output-folder" "avg_attention_matrices/" "--ids-file" "$ids_file" "--root-folder" "$root" "--matrices-folder" "single/matrices/"
python "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "avg_attention_matrices/" "target" "--transformer" "--output-folder" "avg_sentences/"
python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs/" "avg_sentences/" "avg_sentences_sil/"

ls $root/avg_sentences_sil/* > "/home/getalp/zanonbom/eval_acl/average/avg_$id"

