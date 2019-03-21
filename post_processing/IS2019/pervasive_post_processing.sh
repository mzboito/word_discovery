#!/bin/bash

declare -a key=("run2" "run3")
#"run1" "run2" "run3" "run4" "run5")

#source "miniconda3/bin/activate" "miniconda3/envs/transformer_env"

pervasive_folder="$2"
labs="$3"

for k in "${key[@]}"
do
path="$1/$k/"
id="$4"_"$k"


#cd "/home/getalp/zanonbom/attn2d/"
#python "/home/getalp/zanonbom/attn2d/retrieve_attention.py" "-c" "$path/config.yaml" "--output-dir" "$path/attention_matrices/"
cd "$path"
mkdir sentences
mkdir sentences_sil
python "/home/getalp/zanonbom/word_discovery/post_processing/soft2hard.py" "--matrices-prefix" "$path/attention_matrices/final/" "--pervasive" "target" "--output-folder" "sentences/" "--individual-files" "$2/test.ids"
python "/home/getalp/zanonbom/silence_experiments/scripts/remerge_SIL.py" "$labs/" "$path/sentences/" "$path/sentences_sil/"

ls $path/sentences_sil/* > "/home/getalp/zanonbom/eval_acl/pervasive/$id"

done



