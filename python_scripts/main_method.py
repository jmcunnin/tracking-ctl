#!/usr/bin/env python
### Call to method is defined by: python main_method.py arg1=stay_radius arg2=stay_time arg3=warehosue_radius arg4= min_stay
## System stuffs
import sys, sqlite3
## Project stuffs
import tracker, path_object, vizualization

# represents the paths for each truck; Stores as a truck_id::tracker pair
path_dictionary = dict()

database_path =  './database/master.sqlite'


## Implement the tracking modules 
def main(argv):
	#### Pass to tracker class as tables of truck_id
	unique_truckID = []
	try:
		## Set up and find all unique truck id's in master_table
		database = sqlite3.connect(database_path)
		cursor = database.cursor()
		cursor.execute("SELECT DISTINCT truck_id FROM master_table")
		
		unique_truckID = cursor.fetchall()
		unique_truckID = [str(elt[0]) for elt in unique_truckID]

		database.commit()
	except Exception as dbe:
		database.rollback()
		raise dbe
	finally:
		database.close()

	for truck in unique_truckID:
		truck_PO = path_object(truck)
		track_this = tracker(database_path, truck, truck_PO, argv[0], argv[1], argv[2], argv[3], argv[4])
		track_this.compute_tracker
		path_dictionary.update({truck:truck_PO})


	### Need to now store all path objects from the path dictionary
	#### NOTE: this might make more sense during the for loop dependent on how much data we are processing 

	### pass paths to vizualization

if __name__=="__main__":
	main(sys.argv[1:])
