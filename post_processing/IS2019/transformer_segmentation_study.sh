#!/bin/bash

declare -a key=("run1" "run2" "run3" "run4" "run5")
declare -a types=("multi" "single" "avg_last")


for k in "${key[@]}"
  do
  for t in "${type[@]}"
  do
    mkdir "$k/$t"
    mkdir "$k/$t/matrices"
    mkdir "$k/$t/sentences"
    mkdir "$k/$t/sentences_sil"
  done
  mv "$k/attention_matrices/TransformerDecoder/3/EncoderDecoderAttention/*avg*" "$k/avg_last/matrices/"
  python3 "/home/getalp/zanonbom/word_discovery/post_processing/transformer_select2segment.py" "--size" "5130" "--multi" "--single" "--input-root-folder" "$k/attention_matrices/" "--output-dir" "$k/"
  while read line; do
    value=$line
    cp "$k/$value" "$k/single/matrices/"
  done < "$k/singlehead_entropy_list"

  while read line; do
    value=$line
    cp $value "$k/multi/matrices/"
  done < "$k/multihead_entropy_list"
  for t in "${type[@]}"
  do
    python3 "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "$k/$t/matrices/" "--transformer" "True" "target" "--output-folder" "$k/$t/sentences/" "--individual-files" "/home/getalp/zanonbom/xACL/mboshi_5k/files/true_phones/train+dev.ids"
  python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "/home/getalp/zanonbom/attention_study/evaluation/ZRC_corpora/mboshi/5k/graphemic/out/phn/" "$k/$t/sentences/" "$k/$t/sentences_sil/"
  done
done



