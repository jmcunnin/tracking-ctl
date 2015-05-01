#!/usr/bin/env python
import sys
from copy import deepcopy

class trace_object:

	### trace_object is an object to keep track of individual paths
	###### it is defined by a list of stays, a list of trips, and a string identifying it
	def __init__(self, stays, trips, trace_id):
		self.stays = stays
		self.trips = trips
		self.trace_id = trace_id

	############ GETTERS: returning values from the fields ############
	def get_traceID(self):
		return trace_id

	def get_stays(self):
		stay_tuple = tuple(stays)
		return deepcopy(stay_tuple)

	def get_trips(self):
		trips_tuple = tuple(trips)
		return deepcopy(trips_tuple)


