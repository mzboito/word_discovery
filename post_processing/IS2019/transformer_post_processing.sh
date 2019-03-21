#!/bin/bash

#usage root dir files lab id src trg 
declare -a key=("run1" "run2" "run3" "run4" "run5")


transformer_files="$2"
labs="$3"

sourc="$5"
target="$6"

heads=2
layers=3

dict="$transformer_files/test."$sourc

#source "miniconda3/bin/activate" "miniconda3/envs/transformer_env"

for k in "${key[@]}"
do
id="$4"_"$k"
path="$1/$k/"

#cd "/home/getalp/zanonbom/fairseq/"
#python "/home/getalp/zanonbom/fairseq/retrieve_alignment.py" "$transformer_files" "--source-lang" "$sourc" "--target-lang" "$target" "--path" "$path/model/checkpoint_best.pt" "--root-directory" "$path/attention_matrices/" "--gold-source" "$dict"

cd "$path"
mkdir filtered
mkdir sentences
mkdir sentences_sil

python "/home/getalp/zanonbom/word_discovery/post_processing/transformer_select2segment.py" "--output-dir" "$path" "--input-root-folder" "$path/attention_matrices/" "--heads" "$heads" "--layers" "$layers" "--single" "--size" "$7" #> "$path/best_entropy"

while read line; do
 value=$line
 cp $value "$path/filtered/"
done < "singlehead_entropy_list"

python "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "$path/filtered/" "--transformer" "target" "--output-folder" "sentences/" "--individual-files" "$2/test.ids"

python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs/" "$path/sentences/" "$path/sentences_sil/"

ls $path/sentences_sil/* > "/home/getalp/zanonbom/eval_acl/transformer/$id"
done
