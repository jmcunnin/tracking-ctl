#!/usr/bin/env python
import sys
from copy import deepcopy

class truck_path:

	## A path_object is used to store the information about the path of a specific truck
	#### Fields: truck_id (A string representing the truck's id), 
	def __init__(self, truck_id):
		self.truck_id = truck_id
		## Location of stays
		self.stay_set = set()
		## List of tuples, tuples are defined as: (start_time, end_time, start_pos, end_pos)
		self.trips = set()
		### paths set contains trace objects
		self.paths = set()

	############ MUTATORS: adding values to the fields ############
	def add_stay(self, stay, values, begin_time, end_time):
		tup = tuple(stay, values, begin_time, end_time)
		self.stay_set.add(tup)

	def add_trip(self, start_time, end_time, points_list):
		added_tuple = tuple(start_time, end_time, points_list)
		self.trips.append(added_tuple)

	def add_path(self, input_path):
		self.paths.add(input_path)

	def set_warehouse(self, point):
		self.warehouse = point


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
		return self.warehouse




