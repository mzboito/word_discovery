#!/bin/bash
declare -a key=("run1" "run2" "run3") #"run4" "run5")

path_files=$1

src=$3
trg=$4
labs=$5


#source "miniconda3/bin/activate" "miniconda3/envs/tensorflow_env"

for k in "${key[@]}"
do
 path_run="$2/$k/"
 id="$6"_"$k"
 
 cd "/home/getalp/zanonbom/seq2seq/"
 python3 "-m" "translate" "$path_run/config.yaml" "--align" "$path_files/train+dev.$src" "$path_files/train+dev.$trg" "--output" "$path_run/attention_matrices/train+dev"

 cd "$path_run"
 mkdir sentences
 mkdir sentences_sil

 python "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "attention_matrices/train+dev" "target" "--output-folder" "sentences/" "--individual-files" "$path_files/train+dev.ids"

 python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs/" "sentences/" "sentences_sil/"

 ls $path_run/sentences_sil/* > "/home/getalp/zanonbom/eval_acl/mono/$id"
done
