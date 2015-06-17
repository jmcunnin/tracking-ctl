#!/bin/bash

##### File Structure ####
### Main Folder
###### raw_data
######### Files containing the raw data with a .csv extension
######### First row in .csv must contain header names
###### processed_data
######### Files containing the relavent data (truck_id, timestamp, latitude, longitude) as a .csv file
###### database
######### Contain a sqlite database containing the same data as the processed data folder combined into one table called master_table

# Make relavent directories
mkdir -p processed_data
mkdir -p database
mkdir -p raw_already_processed

## Make relavant files
> database/master.sqlite


## Iterate over raw_data folder. Pass file name
for file in ./raw_data/*
do
	python conversion_script.py $file
	filename= basename $file
	mv $file raw_already_processed/$filename
done

stay_radius= 20
stay_time=1
warehouse_radius=140
idle_time=.5
min_warehouse_time=60
max_dest_difference=10

# # python main_method.py $stay_radius $warehouse_radius $stay_time $idle_time $min_warehouse_time $max_dest_difference
python main_method.py  $stay_radius $warehouse_radius $stay_time $idle_time $min_warehouse_time $max_dest_difference


