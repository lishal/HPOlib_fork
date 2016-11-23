#!/bin/bash

#First argument is path to optimizer
#Second argument is openml_tid
#Third argument are seeds
seeds=("$3")
data_seeds=("$4")
seeds=($seeds)
data_seeds=($data_seeds)
let "n_seeds=${#seeds[@]}-1"
echo $n_seeds
export PYTHONPATH=/home/lisha_c_li/HPOlib/
cd /home/lisha_c_li/HPOlib/benchmarks/auto-sklearn/nocv
for i in $(seq 0 $n_seeds)
do
	s=${seeds[$i]}
	d_s=${data_seeds[$i]}
	echo $s
	echo $d_s
	if [ "$1" = "smac/smacnoinit" ]; then
		export searcher="smac/smac"
		sudo PYTHONPATH=$PYTHONPATH HPOlib-run -o ../../../optimizers/$searcher -s $s --HPOLIB:experiment_directory_prefix open_ml_"$2"_data_seed_"$d_s"_noinit_ --SMAC:initialize RANDOM --EXPERIMENT:openml_tid $2 --EXPERIMENT:data_split_seed $d_s
	elif [ "$1" = "tpe/hyperoptnoinit" ]; then
		export searcher="tpe/hyperopt"
		sudo PYTHONPATH=$PYTHONPATH HPOlib-run -o ../../../optimizers/$searcher -s $s --HPOLIB:experiment_directory_prefix open_ml_"$2"_data_seed_"$d_s"_noinit_ --TPE:init 0 --EXPERIMENT:openml_tid $2 --EXPERIMENT:data_split_seed $d_s
	elif [ "$1" = "nvb_hyperband/hyperband_constant" ]; then
		export searcher="nvb_hyperband/nvb_hyperband"
		sudo PYTHONPATH=$PYTHONPATH HPOlib-run -o ../../../optimizers/$searcher -s $s --HPOLIB:experiment_directory_prefix open_ml_"$2"_data_seed_"$d_s"_fixB_ --HYPERBAND:fixb 1 --HYPERBAND:adaptive 1 --EXPERIMENT:openml_tid $2 --EXPERIMENT:data_split_seed $d_s
	else
		export searcher="$1"
		sudo PYTHONPATH=$PYTHONPATH HPOlib-run -o ../../../optimizers/$searcher -s $s --HPOLIB:experiment_directory_prefix open_ml_"$2"_data_seed_"$d_s"_ --EXPERIMENT:openml_tid $2 --EXPERIMENT:data_split_seed $d_s
	fi
	echo $1
	echo $searcher
done