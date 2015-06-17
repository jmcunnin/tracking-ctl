#!/usr/bin/env python
### Call to method is defined by: python main_method.py arg1=stay_radius arg2=stay_time arg3=warehosue_radius arg4= min_stay
## System stuffs
import sys, sqlite3, time
import multiprocessing 
## Project stuffs
from tracker import tracker
from path_object import truck_path
import numpy as np

## This class makes is used to call all of the actual operations that occur (i.e. it primarily is built to call the tracker)
## Implement the tracking modules 
def main(argv):
	global count
	database_path =  './database/master.sqlite'
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

	# Flatten the array and only take unique (issue with sqlite API has ints and strings returned)s
	unique_truckID = [x for inner_arr in set(unique_truckID) for x in inner_arr if isinstance(x, int)]

	### Multi-threaded implementation
	queue = multiprocessing.JoinableQueue()

	num_cpu = multiprocessing.cpu_count()*2
	workers = [QueueWorker(queue) for i in xrange(num_cpu)]
	for worker in workers:
		worker.start()

	for truck in unique_truckID:
		truck_task = Truck_Tracker(argv, database_path, truck)
		queue.put(truck_task)

	for i in xrange(num_cpu):
		queue.put(None)

	try:
		queue.join()
	except KeyboardInterrupt as ke:
		raise RuntimeError("Keyboard Interrupt")

class Truck_Tracker:
	def __init__(self, argv, db_path, truck):
		self.argv = argv
		self.truck = truck
		self.db_path = db_path

	def compute_tracker(self):
		truck_PO = truck_path(self.truck)
		new_tracker = tracker(self.db_path, self.truck, truck_PO, float(self.argv[0]), float(self.argv[1]), float(self.argv[2]), float(self.argv[3]), float(self.argv[4]), float(self.argv[5]))
		new_tracker.compute_tracker()


class QueueWorker(multiprocessing.Process):

	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			task = self.queue.get()
			if task is None:
				self.queue.task_done()
				break
			task.compute_tracker()
			self.queue.task_done()
		return


if __name__=="__main__":
	main(sys.argv[1:])
