#. /home/getalp/zanonbom/miniconda3/bin/activate /home/getalp/zanonbom/miniconda3/envs/transformer_env
#sleep 360
nohup python /home/getalp/zanonbom/attn2d/train.py -c $1/config.yaml --gpu $2 > $1/training_log 2>&1 &
