#!/bin/bash

root=$1
labs=$2
id=$3

cd "$root"
echo $root
mkdir avg_sentences
mkdir avg_sentences_sil


python "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "avg_attention_matrices/" "target" "--output-folder" "avg_sentences/"

python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs/" "avg_sentences/" "avg_sentences_sil/"
ls $root/avg_sentences_sil/* > "/home/getalp/zanonbom/eval_acl/average/avg_$id"
