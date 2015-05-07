#!/usr/bin/env python
import sys, sqlite3, math

from path_object import truck_path
from copy import deepcopy
import math as m
from filter_jumps import filter_noise

class tracker:


	def __init__(self, database_path, truck_id, path, stay_radius, warehouse_radius, min_stay_time, max_idle_time, min_warehouse_time, max_dest_difference):
		## string representing the path to the database
		self.db_path = str(database_path)
		## String representing the name of the values with the truck_id
		## The path_object used to store the path
		self.path = path

		### Tuneable parameters
		self.truck_id = truck_id
		self.stay_time = min_stay_time
		self.stay_radius = stay_radius
		self.warehouse_radius = warehouse_radius
		self.min_stay_time = min_stay_time
		self.min_warehouse_time = min_warehouse_time
		self.max_idle_time = max_idle_time
		self.max_dest_difference = max_dest_difference
		self.data = list()

	def calculate_warehouse(self):
		## calculate the storage center/s and store to path_object
		i = 0
		while i < len(self.data):
			j = i
			i_time = self.data[i][2]
			while j < len(self.data):
				if(self.time_difference(self.data[j][2], i_time) > self.min_warehouse_time):
					break
				j += 1
			## Get the list of points across which we figure out our stay radius
			curr_list = [tuple((elt[0], elt[1])) for elt in self.data[i:j]]
			if self.diameter(curr_list) > self.warehouse_radius:
				i += 1
			else:
				while j < len(self.data)-1:
					new_list = curr_list + [tuple((self.data[j+1][0], self.data[j+1][1]))]
					if self.diameter(new_list) <= self.warehouse_radius:
						curr_list = new_list
						j += 1
					else:
						break

				self.path.add_warehouse(self.medoid(curr_list))
				i = j + 1


	
	def calculate_stays(self):
		## Calculate our stays here and add to the path_object
		i = 0
		while i < len(self.data):
			j = i
			i_time = self.data[i][2]
			while j < len(self.data):
				if(self.time_difference(self.data[j][2], i_time) > self.min_stay_time):
					break
				j += 1
			## Get the list of points across which we figure out our stay radius
			curr_list = [tuple((elt[0], elt[1])) for elt in self.data[i:j]]
			if self.diameter(curr_list) > self.stay_radius:
				i += 1
			else:
				while j < len(self.data)-1:
					new_list = curr_list + [tuple((self.data[j+1][0], self.data[j+1][1]))]
					if self.diameter(new_list) <= self.stay_radius:
						curr_list = new_list
						j += 1
					else:
						break
				try:
					self.path.add_stay(self.medoid(curr_list), self.data[i:j], self.data[i][2], self.data[j][2])
				except IndexError as ie:
					self.path.add_stay(self.medoid(curr_list), self.data[i:j-1], self.data[i][2], self.data[j-1][2])
				i = j + 1




	def calculate_trips(self):
		## Calculate our trips here and add to the path_object
		stays = self.path.get_stays()
		warehouses = self.path.get_warehouse()
		
		if len(stays) == 0:
			raise RuntimeError("No stays calculated. Reprametrize")

		## Add a trip object if the first stay does not occur until after the start of the data
		current_trip = []
		for stay in stays:
			stay_at_warehouse = self.in_warehouse(stay[0], warehouses)
			if stay_at_warehouse:
				if not len(current_trip) is 0:
					self.path.add_trip(deepcopy(current_trip))
					current_trip[:] = []
			else:
				current_trip.append(stay[0])


	def in_warehouse(self, point, warehouses):
		for warehouse in warehouses:
			if self.distance(point, warehouse) < self.warehouse_radius:
				return True
		return False



	def calculate_destinations(self):
		stays = self.path.get_stays()
		stays_copy = deepcopy(stays)

		while len(stays_copy) is not 0:
			dest = []
			pt = stays_copy.pop()
			dest.append(pt[0])
			while(True):
				min_pt = self.min_distance_pt(pt[0], stays_copy)
				if min_pt is None:
					break
				elif self.distance(pt[0], min_pt[0]) <= self.max_dest_difference:
					dest.append(min_pt[0])
					stays_copy.remove(min_pt)
				else:
					break
			med = self.medoid(dest)
			self.path.add_destination(med, dest)

	def min_distance_pt(self, point, list_pts):
		min_dist = 10000000
		current_best_pt = None
		for pt in list_pts:
			dist = self.distance(point, pt[0])
			if dist < min_dist:
				current_best_pt = pt
				min_dist = dist

		return current_best_pt
	
	def stay_contains_warehouse(self, point, warehouses):
		assert type(warehouses) == type([])
		assert type(point) == type((0,0))
		try:
			for warehouse in warehouses:
				if self.distance(point, warehouse) < warehouse_radius:
					return True
			return False
		except TypeError as te:
			return False 

	## Computes the difference in the two times in minutes
	def time_difference(self, time1, time2):
		## Array = [day, month, year, hour, minute, second]
		time1_arr = [int(time1[0:2]), int(time1[3:5]), int(time1[6:10]), int(time1[11:13]), int(time1[14:16]), int(time1[17:19])]
		time2_arr = [int(time2[0:2]), int(time2[3:5]), int(time2[6:10]), int(time2[11:13]), int(time2[14:16]), int(time2[17:19])]

		difference = 0.0
		difference += (time1_arr[0] - time2_arr[0])*1440.
		difference += (time1_arr[1] - time2_arr[1])*43829.
		difference += (time1_arr[2] - time2_arr[2])*525949.
		difference += (time1_arr[3] - time2_arr[3])*60.
		difference += (time1_arr[4] - time2_arr[4])
		difference += (time1_arr[4] - time2_arr[4])/60.
		return difference


	def distance(self, pt1, pt2):
		earth_radius = 6371000.  ## Radius in meters
		pt1_x = earth_radius*m.cos(float(pt1[0]))*m.cos(float(pt1[1]))
		pt1_y = earth_radius*m.cos(float(pt1[0]))*m.sin(float(pt1[1]))
		pt1_z = earth_radius*m.sin(float(pt1[0]))

		pt2_x = earth_radius*m.cos(float(pt2[0]))*m.cos(float(pt2[1]))
		pt2_y = earth_radius*m.cos(float(pt2[0]))*m.sin(float(pt2[1]))
		pt2_z = earth_radius*m.sin(float(pt2[0]))

		return pow((pow((pt1_x - pt2_x), 2) + pow((pt1_y - pt2_y), 2) + pow((pt1_y - pt2_y), 2)), .5)

	## Computes the medoid over a set of points
	#### The medoid is defined as the point in a set of data that minimizes the overall distance to all other points
	def medoid(self, points):
		best_point = None ## best_point[0] = point, best_point[1] = sum
		min_sum = 10000000000 ## basically setting to infinity and improving
		
		for elt1 in points:
			i_sum = 0
			for elt2 in points:
				if elt1 != elt2:
					i_sum += self.distance(elt1, elt2)
			if i_sum < min_sum:
				best_point = elt1
				min_sum = i_sum
		
		if best_point != None:
			return best_point
		else:
			raise RuntimeError("Issue computing medoid. Returned a medoid of 0")

	## Computes the maximum diameter over a set of points
	def diameter(self, points):
		biggest_diameter = 0
		for pt1 in points:
			pt1_max_diam = 0
			for pt2 in points:
				if pt1 != pt2:
					intermediate_diameter = self.distance(pt1, pt2)
					if intermediate_diameter > pt1_max_diam:
						pt1_max_diam = intermediate_diameter
			if pt1_max_diam > biggest_diameter:
				biggest_diameter = pt1_max_diam
		return biggest_diameter


	def compute_tracker(self):
		try:
			database = sqlite3.connect(self.db_path)
			database.text_factory = str
			curs = database.cursor()

			curs.execute("""SELECT latitude, longitude, timestamp FROM master_table WHERE carrier_ID=?""", [str(self.truck_id[0])])
			self.data = curs.fetchall()
			
			database.commit()
		except Exception as dbe:
			print "Something went wrong with the database in tracker.py"
			database.rollback()
			raise dbe
		finally:
			database.close()

		## This line filters out all outlying data (i.e. any jumps over 150 kph)
		# self.data = filter_noise(self.data, 150.).filter()

		## Calculate stays and store to SQL
		self.calculate_stays()
		self.path.store_stays_to_SQL(self.db_path)

		self.calculate_warehouse()
		self.path.store_warehouses_to_SQL(self.db_path)
		
		self.calculate_trips()
		self.path.store_trips_to_SQL(self.db_path)	
		
		self.calculate_destinations()
		self.path.store_destinations_to_SQL(self.db_path)






