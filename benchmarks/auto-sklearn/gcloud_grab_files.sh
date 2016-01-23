#!/bin/bash
output=$(gcloud compute instance-groups managed list-instances instance-group-1 --zone us-central1-f | cut -d' ' -f1)
instances_list=($output)
let "n=${#instances_list[@]}-1"
cd /home/lisha/school/Hyperband/benchmarks
for k in $(seq 1 $n); do 
	ssh -t ${instances_list[$k]}.us-central1-f.stately-will-107018 "sudo chmod -R 666 /home/lisha_c_li/HPOlib/benchmarks/auto-sklearn/nocv/*/open_ml*.pkl" 
done
wait
for k in $(seq 1 $n); do 
	rsync -a -f"+ */" -f"+ open_ml*.pkl" -f"- *" ${instances_list[$k]}.us-central1-f.stately-will-107018:/home/lisha_c_li/HPOlib/benchmarks/auto-sklearn/nocv/ autosklearn/cv
done
wait
