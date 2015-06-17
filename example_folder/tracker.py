#!/usr/bin/env python
import  sqlite3, multiprocessing
from path_object import truck_path
from copy import deepcopy
import math as m
from filter_jumps import filter_noise




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
	#
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
			while (True):
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
		corrections = [1440., 43829., 525949., 60., 1, 1 / 60]

		return sum([(t1 - t2) * corr for t1, t2, corr in zip(time1_arr, time2_arr, corrections)])

	def distance(self, pt1, pt2):
		earth_radius = 6371000.  ## Radius in meters
		pt1_x = earth_radius * m.cos(float(pt1[0])) * m.cos(float(pt1[1]))
		pt1_y = earth_radius * m.cos(float(pt1[0])) * m.sin(float(pt1[1]))
		pt1_z = earth_radius * m.sin(float(pt1[0]))

		pt2_x = earth_radius * m.cos(float(pt2[0])) * m.cos(float(pt2[1]))
		pt2_y = earth_radius * m.cos(float(pt2[0])) * m.sin(float(pt2[1]))
		pt2_z = earth_radius * m.sin(float(pt2[0]))

		return pow((pow((pt1_x - pt2_x), 2) + pow((pt1_y - pt2_y), 2) + pow((pt1_y - pt2_y), 2)), .5)

	## This computes the haversine distance as opposed to the law of cos. If you wish to switch, change header to distance and above to something else
	# def haversine_dist(self, pt1, pt2):
	# 	lat1, lon1 = pt1
	# 	lat2, lon2 = pt2
	# 	lst = [lat1, lon1, lat2, lon2]
	# 	lat1, lon1, lat2, lon2 = map(m.radians, [float(x) for x in lst])
     #
	# 	dlon = lon2 - lon1
	# 	dlat = lat2 - lat1
     #
	# 	a = m.sin(dlat/2)**2 + m.cos(lat1) * m.cos(lat2) * m.sin(dlon/2)**2
	# 	c = 2 * m.asin(m.sqrt(a))
	# 	return (6367 * c) * 1000

	## Computes the medoid over a set of points
	#### The medoid is defined as the point in a set of data that minimizes the overall distance to all other points
	def medoid(self, points):
		best_point = None  ## best_point[0] = point, best_point[1] = sum
		min_sum = 10000000000  ## basically setting to infinity and improving

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

	def compute_tracker(self):
		global process_count
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

		# # This line filters out all outlying data (i.e. any jumps over 150 kph)
		# # self.data = filter_noise(self.data, 150.).filter()
		## Calculate stays and store to SQL

		### Multi-threaded
        #
		# queue = multiprocessing.JoinableQueue()
		# workers = [Worker(queue) for i in xrange(2)] ## warehouse and stay computed
		# for w in workers:
		# 	w.start()
        #
		# stay_proc = Compute_Stays_Thread(self, self.path, self.db_path)
		# queue.put(stay_proc)
        #
		# warehouse_proc = Compute_Warehouse_Thread(self, self.path, self.db_path)
		# queue.put(warehouse_proc)
        #
		# queue.put(None)
		# queue.put(None)
        #
		# try:
		# 	queue.join()
		# except KeyboardInterrupt as ke:
		# 	raise RuntimeError("Keyboard Interrupt")
		### End multi-threaded


		#### Single Threaded Implementation
		self.calculate_stays()
		self.path.store_stays_to_SQL(self.db_path)

		self.calculate_warehouse()
		self.path.store_warehouses_to_SQL(self.db_path)
		#### End Single Threaded Implementation

		self.calculate_trips()
		self.path.store_trips_to_SQL(self.db_path)

		self.calculate_destinations()
		self.path.store_destinations_to_SQL(self.db_path)


	def set_data_test(self, test_data):
		self.data = test_data


# # ## Helper classes used by the multi-threaded implementation to split up stay and warehouse calculation.
# class Compute_Stays_Thread():
# 	def __init__(self, tracker, path, db_path):
# 		self.tracker = tracker
# 		self.path_object = path
# 		self.db_path = db_path
#
# 	def compute(self):
# 		self.tracker.calculate_stays()
# 		self.path_object.store_stays_to_SQL(self.db_path)
# 		return
#
#
#
# class Compute_Warehouse_Thread():
# 	# global warehouse_status
# 	def __init__(self, tracker, path, db_path):
# 		self.tracker = tracker
# 		self.path_object = path
# 		self.db_path = db_path
# 		self.curr_stat = False
#
# 	def compute(self):
# 		self.tracker.calculate_warehouse()
# 		self.path_object.store_warehouses_to_SQL(self.db_path)
# 		return
#
# class Worker(multiprocessing.Process):
# 	def __init__(self, queue):
# 		multiprocessing.Process.__init__(self)
# 		self.queue = queue
#
# 	def run(self):
# 		while True:
# 			task = self.queue.get()
# 			if task is None:
# 				self.queue.task_done()
# 				break
# 			task.compute()
# 			self.queue.task_done()
# 		return








