#!/usr/bin/env python
### Call to method is defined by: python main_method.py arg1=stay_radius arg2=stay_time arg3=warehosue_radius arg4= min_stay
## System stuffs
import sys, sqlite3
## Project stuffs
from tracker import tracker
from path_object import truck_path

# represents the paths for each truck; Stores as a truck_id::tracker pair
path_dictionary = dict()

database_path =  './database/master.sqlite'


def store_to_sql():
	for truck in path_dictionary.keys():
		path_dictionary[truck].store_to_sql(path_object_path)


## Implement the tracking modules 
def main(argv):
	#### Pass to tracker class as tables of truck_id
	unique_truckID = []
	try:
		## Set up and find all unique truck id's in master_table
		database = sqlite3.connect(database_path)
		database.text_factory = str
		cursor = database.cursor()
		
		cursor.execute("SELECT DISTINCT truck_id FROM master_table")
		unique_truckID = cursor.fetchall()

		database.commit()
	except Exception as dbe:
		database.rollback()
		raise dbe
	finally:
		database.close()

	for truck in unique_truckID:
		truck_PO = truck_path(truck)
		# track_this = tracker(database_path, truck[0], truck_PO, 1000, 1000, 2, .5, 60)
		track_this = tracker(database_path, truck, truck_PO, float(argv[0]), float(argv[1]), float(argv[2]), float(argv[3]), float(argv[4]), float(argv[5]))
		track_this.compute_tracker()
		# track_this.compute_tracker()
		path_dictionary.update({truck[0]:truck_PO})
		

if __name__=="__main__":
	print sys.argv[1:]
	main(sys.argv[1:])
