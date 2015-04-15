#!/usr/bin/env python
import sys
from copy import deepcopy

class truck_path:



	## A path_object is used to store the information about the path of a specific truck
	#### Fields: truck_id (A string representing the truck's id), 
	def __init__(self, truck_id):
		self.truck_id = truck_id
		## Location of stays
		self.stay_set = list()
		## List of tuples, tuples are defined as: (start_time, end_time, start_pos, end_pos)
		self.trips = list()
		### paths set contains trace objects
		self.paths = list()
		self.warehouses = list()

	############ MUTATORS: adding values to the fields ############
	def add_stay(self, stay, values, begin_time, end_time):
		tup = (stay, values, begin_time, end_time)
		self.stay_set.append(tup)

	def add_trip(self, start_time, end_time, points_list):
		added_tuple = (start_time, end_time, points_list)
		self.trips.append(added_tuple)

	def add_path(self, input_path):
		self.paths.append(input_path)

	def add_warehouse(self, point):
		self.warehouses.append(point)


	############ GETTERS: returning values from the fields ############
	def get_stays(self):
		return deepcopy(self.stay_set)

	def get_trips(self):
		return deepcopy(self.trips)

	def get_paths(self):
		return deepcopy(self.paths)

	def get_truckID(self):
		return self.truck_id

	def get_warehouse(self):
		return deepcopy(self.warehouses)


	#### Storing to SQL:
	def store_to_sql(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			cursor.execute('CREATE TABLE IF NOT EXISTS ? (object_type, object_number, object_sub_type, object_value, start_time, end_time', [self.truck_id])

			current_object = 'stay'
			object_number = 0

			for stay in self.stay_set:
				cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'location', stay[0], stay[2], stay[3]]])
				for point in stay[1]:
					cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'point', [point[0], point[1]], point[2], point[2]]])

				object_number += 1

			current_object = 'trip'
			object_number = 0

			for path in self.trips:
				cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'start', path[2][0], path[0], path[0]]])
				cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'end', path[2][-1], path[1], path[1]]])
				for point in path[2]:
					cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'point', [point[0], point[1]], point[2], point[2]]])
				object_number += 1

			current_object = 'warehouse'
			object_number = 0

			for warehouse in self.warehouses:
				cursor.execute('INSERT INTO ? VALUES ?', [self.truck_id, [current_object, object_number, 'warehouse', warehouse, 'NULL', 'NULL'])


		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()





