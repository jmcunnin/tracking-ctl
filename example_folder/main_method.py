#!/usr/bin/env python
### Call to method is defined by: python main_method.py arg1=stay_radius arg2=stay_time arg3=warehosue_radius arg4= min_stay
## System stuffs
import sys, sqlite3
import multiprocessing 
## Project stuffs
from tracker import tracker
from path_object import truck_path
import numpy as np

## This class makes is used to call all of the actual operations that occur (i.e. it primarily is built to call the tracker)

database_path =  './database/master.sqlite'

## Implement the tracking modules 
def main(argv):
	#### Pass to tracker class as tables of truck_id
	unique_truckID = []
	try:
		## Set up and find all unique truck id's in master_table
		database = sqlite3.connect(database_path)
		database.text_factory = str
		cursor = database.cursor()

		## Create the necessary tables
		cursor.execute("CREATE TABLE IF NOT EXISTS  stays (carrier_ID, stay_count, stay_lat, stay_long, related_latitude, related_longitude, begin_time, end_time )")
		cursor.execute("CREATE TABLE IF NOT EXISTS warehouses (carrier_ID, latitude, longitude)")
		cursor.execute("CREATE TABLE IF NOT EXISTS trips (carrier_ID, trip_count, value_lat, value_long)")
		cursor.execute("CREATE TABLE IF NOT EXISTS destinations (carrier_ID, dest_count, stay_lat, stay_long, related_latitude, related_longitude)")
		
		cursor.execute("SELECT DISTINCT carrier_ID FROM master_table")
		unique_truckID = cursor.fetchall()

		database.commit()
	except Exception as dbe:
		database.rollback()
		raise dbe
	finally:
		database.close()


	###### Single-Threaded implementation
	# for truck in unique_truckID:
	# 	truck_PO = truck_path(truck)
	# 	track_this = tracker(database_path, truck, truck_PO, float(argv[0]), float(argv[1]), float(argv[2]), float(argv[3]), float(argv[4]), float(argv[5]))
	# 	track_this.compute_tracker()


	#### Multi-threaded implementation
	num_divisions = 4
	sub_arrs = np.array_split(unique_truckID, num_divisions)
	processes = []
	
	for sub_arr in sub_arrs:
		proc = Truck_Tracker(argv, database_path, sub_arr)
		processes += [proc]
		proc.start()

	try:
		while True:
			## continue doing this unless we get an interrupt
			pass
	except KeyboardInterrupt:
		for proc in processes:
			thr.terminate()

	for proc in processes:
		proc.join()


class Truck_Tracker(multiprocessing.Process):
	def __init__(self, argv, db_path, truck_sub_array):
		multiprocessing.Process.__init__(self)
		self.argv = argv
		self.sub_array = truck_sub_array
		self.db_path = db_path

	def run(self):
		for truck in self.sub_array:
			truck_PO = truck_path(truck)
			new_tracker = tracker(self.db_path, truck, truck_PO, float(self.argv[0]), float(self.argv[1]), float(self.argv[2]), float(self.argv[3]), float(self.argv[4]), float(self.argv[5]))
			new_tracker.compute_tracker()

if __name__=="__main__":
	print sys.argv[1:]
	main(sys.argv[1:])
