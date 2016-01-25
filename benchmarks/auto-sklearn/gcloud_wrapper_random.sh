#!/bin/bash
output=$(gcloud compute instance-groups managed list-instances instance-group-1 --zone us-central1-f | cut -d' ' -f1)
instances_list=($output)
tids=(2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 20 21 22 23 24 26 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 47 48 49 50 52 53 54 55 57 58 59 60 2065 2073 2074 2075 2078 2079 3022)
seeds="1 5001 10001 15001 20001 25001 30001 35001 40001 45001"
seeds2="50001 55001 60001 65001 70001 75001 80001 85001 90001 95001"
seeds3="100001 105001 110001 115001 120001 125001 130001 135001 140001 145001"

for k in $(seq 1 171); do 
	let "optimizer=($k-1)%3"
	let "tid = ($k-1)/3"
	echo $optimizer
	echo $tid
	if [ $optimizer -eq 0 ]; then
		gcloud compute ssh lisha_c_li@${instances_list[$k]} --zone us-central1-f --command "cd /home/lisha_c_li; screen -dm ./experiment_loop.sh tpe/random_hyperopt ${tids[$tid]} \"$seeds\" \"$seeds\"" 
	fi
	if [ $optimizer -eq 1 ]; then
		gcloud compute ssh lisha_c_li@${instances_list[$k]} --zone us-central1-f --command "cd /home/lisha_c_li; screen -dm ./experiment_loop.sh tpe/random_hyperopt ${tids[$tid]} \"$seeds2\" \"$seeds\"" 
	fi
	if [ $optimizer -eq 2 ]; then
		gcloud compute ssh lisha_c_li@${instances_list[$k]} --zone us-central1-f --command "cd /home/lisha_c_li; screen -dm ./experiment_loop.sh tpe/random_hyperopt ${tids[$tid]} \"$seeds3\" \"$seeds\"" 
	fi
done
wait