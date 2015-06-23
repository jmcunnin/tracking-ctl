#!/usr/bin/env python
import  sqlite3
from path_object import truck_path
from copy import deepcopy
import math as m
from filter_jumps import filter


INFINITY = "INF" ## Only works with Python 2.x, upgrade for 3

class tracker:


	def __init__(self, database_path, truck_id, path, stay_radius, warehouse_radius, min_stay_time, max_idle_time,
				 min_warehouse_time, max_dest_difference):
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

	#############
	# Method used to calculate the relative warehouses for the truck path
	# Modifies the warehosue field of the path object associated with the call to trackers
	def calculate_warehouse(self):
		## calculate the storage center/s and store to path_object
		i = 0
		while i < len(self.data):
			j = i
			i_time = self.data[i][2]
			while j < len(self.data):
				if (self.time_difference(self.data[j][2], i_time) > self.min_warehouse_time):
					break
				j += 1
			## Get the list of points across which we figure out our stay radius
			curr_list = [tuple((elt[0], elt[1])) for elt in self.data[i:j]]
			if self.diameter(curr_list) > self.warehouse_radius:
				i += 1
			else:
				while j < len(self.data) - 1:
					new_list = curr_list + [tuple((self.data[j + 1][0], self.data[j + 1][1]))]
					if self.diameter(new_list) <= self.warehouse_radius:
						curr_list = new_list
						j += 1
					else:
						break

				self.path.add_warehouse(self.medoid(curr_list))
				i = j + 1

	############
	# Method used to calculate the relative stays for the truck's path
	# Modifies the stays field of the path object associated with the call to trackers
	def calculate_stays(self):
		## Calculate our stays here and add to the path_object
		i = 0
		while i < len(self.data):
			j = i
			i_time = self.data[i][2]
			while j < len(self.data):
				if (self.time_difference(self.data[j][2], i_time) > self.min_stay_time):
					break
				j += 1
			## Get the list of points across which we figure out our stay radius
			curr_list = [tuple((elt[0], elt[1])) for elt in self.data[i:j]]
			if self.diameter(curr_list) > self.stay_radius:
				i += 1
			else:
				while j < len(self.data) - 1:
					new_list = curr_list + [tuple((self.data[j + 1][0], self.data[j + 1][1]))]
					if self.diameter(new_list) <= self.stay_radius:
						curr_list = new_list
						j += 1
					else:
						break
				try:
					self.path.add_stay(self.medoid(curr_list), self.data[i:j], self.data[i][2], self.data[j][2])
				except IndexError as ie:
					self.path.add_stay(self.medoid(curr_list), self.data[i:j - 1], self.data[i][2], self.data[j - 1][2])
				i = j + 1

	############
	# Method used to calculate the points associated with the trips between the stays
	# A trip is defined as the series of points in the path, bifurcated by the stays, This was inferred, but not explicit from Proj. Lachesis
	def calculate_trips(self):
		## Calculate our trips here and add to the path_object
		raw_dat = [x[0:2] for x in self.data]
		stays = self.path.get_stays()
		stay_marker = [x[0] for x in stays]

		warehouses = self.path.get_warehouse()
		if len(stays) == 0:
			raise RuntimeError("No stays calculated. Reprametrize")

		## Add a trip object if the first stay does not occur until after the start of the data
		i = 0
		curr_trip = list()
		for val in raw_dat:
			if (i < len(stay_marker)) and (val == stay_marker[i]):
				self.path.add_trip(deepcopy(curr_trip))
				i+=1
				curr_trip = []
			else:
				curr_trip.append(deepcopy(val))
		self.path.add_trip(curr_trip)




	def in_warehouse(self, point, warehouses):
		for warehouse in warehouses:
			if self.distance(point, warehouse) < self.warehouse_radius:
				return True
		return False

	def calculate_destinations(self):
		locs = [(x[0], x[1]) for x in self.data]

		### Combine all duplicated points
		dests = dict()
		counts = dict((i , locs.count(i)) for i in locs)
		for key in counts:
			dests[key] = [key for i in xrange(counts[key])]

		while True:
			locs = deepcopy(dests.keys())
			closest_pair = self.find_closest(locs)
			if len(closest_pair) is 1:
				break
			if closest_pair[2] > self.max_dest_difference:
				break

			combined = dests[closest_pair[0]] + dests[closest_pair[1]]
			del dests[closest_pair[0]]
			del dests[closest_pair[1]]

			medoid = self.medoid(combined)
			dests[medoid] = combined

		MIN_PTS_FOR_DEST = 5
		for dest in dests.keys():
			if len(dests[dest]) > MIN_PTS_FOR_DEST:
				self.path.add_destination(dest, dests[dest])

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
		assert type(point) == type((0, 0))
		try:
			for warehouse in warehouses:
				if self.distance(point, warehouse) < self.warehouse_radius:
					return True
			return False
		except TypeError as te:
			return False

		## Computes the difference in the two times in minutes

	def time_difference(self, time1, time2):
		## Array = [day, month, year, hour, minute, second]
		time1_arr = [int(time1[0:2]), int(time1[3:5]), int(time1[6:10]), int(time1[11:13]), int(time1[14:16]),
					 int(time1[17:19])]
		time2_arr = [int(time2[0:2]), int(time2[3:5]), int(time2[6:10]), int(time2[11:13]), int(time2[14:16]),
					 int(time2[17:19])]
		## Minutes per: day, month, year, hour, minute, second
		corrections = [1440., 43829., 525949., 60., 1., 1. / 60.]

		return sum([(t1 - t2) * corr for t1, t2, corr in zip(time1_arr, time2_arr, corrections)])

	## Computes the haversine distance
	def distance(self, pt1, pt2):
		earth_radius = 6371000.  ## Radius in meters
		lst = [pt1[0], pt1[1], pt2[0], pt2[1]]
		lat1, lon1, lat2, lon2 = map(m.radians, [float(x) for x in lst])

		a = m.sin((lat2 - lat1)/2)**2 + m.cos(lat1) * m.cos(lat2) * m.sin((lon2 - lon1)/2)**2
		c = 2 * m.asin(m.sqrt(a))
		return c * earth_radius

	## Computes the medoid over a set of points
	#### The medoid is defined as the point in a set of data that minimizes the overall distance to all other points
	def medoid(self, points):
		best_point = None
		min_sum = INFINITY

		for elt1 in points:
			i_sum = sum([self.distance(x, elt1) for x in points])
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
			pt1_max_diam = max([self.distance(x, pt1) for x in points])
			if pt1_max_diam > biggest_diameter:
				biggest_diameter = pt1_max_diam
		return biggest_diameter

	def find_closest(self, points):
		min_dist = INFINITY
		curr_best = points[0]
		match = None
		for outer_pt in points:
			for inner_pt in points:
				if outer_pt != inner_pt:
					curr_dist = self.distance(inner_pt, outer_pt)
					if curr_dist < min_dist:
						min_dist = curr_dist
						curr_best = outer_pt
						match = inner_pt
		return [curr_best, match, min_dist]

	def compute_tracker(self):
		try:
			database = sqlite3.connect(self.db_path)
			database.text_factory = str
			curs = database.cursor()

			curs.execute("""SELECT latitude, longitude, timestamp FROM master_table WHERE carrier_ID=?""",
						 [str(self.truck_id)])
			self.data = curs.fetchall()

			database.commit()
		except Exception as dbe:
			print "Something went wrong with the database in tracker.py"
			database.rollback()
			raise dbe
		finally:
			database.close()

		### This line filters out all outlying data (i.e. any jumps over 150 kph)
		### Uncomment for usage.
		# print "Filtering any truck jumps for: " + str(self.truck_id)
		# self.data = filter(self.data, 150.)



		## Calculate stays and store to SQL

		self.calculate_stays()
		self.path.store_stays_to_SQL(self.db_path)

		self.calculate_warehouse()
		self.path.store_warehouses_to_SQL(self.db_path)

		self.calculate_trips()
		self.path.store_trips_to_SQL(self.db_path)

		self.calculate_destinations()
		self.path.store_destinations_to_SQL(self.db_path)










