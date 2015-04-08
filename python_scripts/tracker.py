#!/usr/bin/env python
import sys, path_object, sqlite3, math

class tracker:


	def __init__(self, database_path, truck_id, path, stay_radius, warehouse_radius, min_stay_time, max_idle_time, min_warehouse_time):
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
		self.min_warehouse_time = min_warehouse_time
		self.max_idle_time = max_idle_time
		self.data = list()

	# def calculate_warehouse(self):
	# 	## calculate the storage center/s and store to path_object
	# 	i = 0
	# 	while i < len(self.data):
	# 		j = i
	# 		i_time = self.data[i][2]
	# 		while(True):
	# 			if((self.data[j][2] - i_time) > self.min_warehouse_time):
	# 				break
	# 			j += 1
	# 		curr_list = [tuple(elt[0], elt[1]) for elt in self.data[i:j]]
	# 		if diameter(curr_list) > self.warehouse_radius:
	# 			i += 1
	# 		else:
	# 			while(diameter(curr_list) <= self.warehouse):
	# 				j += 1
	# 				curr_list.append(tuple(self.data[j][0], self.data[j][1]))
	# 			best_point = medoid(curr_list)
	# 			best_point = [elt for elt in self.data[i:j] if (best_point[0] is elt[0] and best_point[1] is elt[1])]
	# 			best_point = best_point[0]
	# 			self.warehouse = best_point
	# 			i = j + 1


	# def calculate_stays(self):
	# 	## Calculate our stays here and add to the path_object
	# 	i = 0
	# 	while i < len(self.data):
	# 		j = i
	# 		i_time = self.data[i][2]
	# 		while(True):
	# 			if((self.data[j][2] - i_time) > self.min_stay_time):
	# 				break
	# 			j += 1
	# 		curr_list = [tuple(elt[0], elt[1]) for elt in self.data[i:j]]
	# 		if diameter(curr_list) > self.stay_radius:
	# 			i += 1
	# 		else:
	# 			while(diameter(curr_list) <= self.stay_radius):
	# 				j += 1
	# 				curr_list.append(tuple(self.data[j][0], self.data[j][1]))
	# 			best_point = medoid(curr_list)
	# 			best_point = [elt for elt in self.data[i:j] if (best_point[0] is elt[0] and best_point[1] is elt[1])]
	# 			best_point = best_point[0]
	# 			new_stay = [elt for elt in self.data[i:j]]
	# 			self.path.add_stay(best_point, new_stay, self.data[i][2], self.data[j][2])
	# 			i = j + 1




	# def calculate_trips(self):
	# 	## Calculate our trips here and add to the path_object
	# 	calculated_stays = self.path.get_stays()
	# 	paths = []
	# 	i = 0
	# 	if calculated_stays[0][2] is not self.data[0][2]:
	# 		j = 0
	# 		while(calculated_stays[0][2] is not self.data[j][2]):
	# 			j += 1
	# 		self.path.add_trip(self.data[0][2], self.data[j][2]), self.data[i:j])
	# 		i = j
	# 	while i < len(self.data):
	# 		j = i + 1
	# 		while(calculate_stays[i + 1][3] is not self.data[j][2]):
	# 			j += 1
	# 		self.path.add_trip(self.data[i][2], self.data[j][2], self.data[i:j])
	# 		i = j



	# def calculate_paths(self):
	# 	## Calculate our paths, store as a trace object and add to the path_object
	# 	calculated_stays = self.path.get_stays()
	# 	calculated_trips = self.path.get_paths()
	# 	stay_first = (calculated_stays[0][2] < calculated_trips[0][1])		
	# 	i = 0
	# 	while(0 < len(calculate_stays)):
	# 		trace_stays = []
	# 		trace_trips = []
	# 		if i is 0 and not stay_first:
	# 			trace_trips.add(calculated_trips.pop(0))
	# 		while(not stay_contains_warehouse(self.warehouse, calculate_stays[0])):
	# 			trace_stays.add(calculate_stays.pop(0))
	# 			trace_trips.add(calculate_trips.pop(0))
	# 		i += 1
	# 		trace =trace_object(trace_stays, trace_trips, i)
	# 		self.path.add_path(trace)

	
	# def stay_contains_warehouse(self, warehouse, calculate_stays):
	# 	sum_in_radius = 0.0
	# 	for stay in calculate_stays:
	# 		if not (distance(warehouse[0], warehouse[1], stay[1][0], stay[1]) < self.warehouse_radius):
	# 			sum_in_radius += 1.
	# 	return (float(len(calculate_stays))/sum_in_radius < .2)


	# def time_difference(self, time1, time2):
	# 	## Array = [day, month, year, hour, minute, second]
	# 	time1_arr = [time1[0:2], time1[3:5], time1[6:10], time1[11:13], time1[14:16], time1[17:19]]
	# 	time2_arr = [time2[0:2], time2[3:5], time2[6:10], time2[11:13], time2[14:16], time2[17:19]]

	
	# def distance(self, x1, y1, x2, y2):
	# 	return pow(pow((x1-x2), 2) + pow((y1-y2), 2), .5)

	# def medoid(self, points):
	# 	best_point = (0, 0) ## best_point[0] = point best_point[1] = sum
	# 	i = 0
	# 	while i < len(points):
	# 		i_sum = 0
	# 		i_x = points[i][0]
	# 		i_y = points[i][1]
	# 		j = 0
	# 		while j < len(points):
	# 			j_x = points[j][0]
	# 			j_y = points[j][1]
	# 			if i is not j:
	# 				i_sum += distance(i_x, i_y, j_x, j_y)
	# 			j += 1
	# 		if i_sum < best_point[1]:
	# 			best_point = (points[i], i_sum)
	# 		i += 1
	# 	return best_point[0]

	# def diameter(self, points):
	# 	diameter = 0
	# 	i = 0
	# 	while i < len(points):
	# 		biggest_diameter = 0
	# 		i_x = points[i][0]
	# 		i_y = points[i][1]
	# 		j = 0
	# 		while j < len(points):
	# 			j_x = points[j][0]
	# 			j_y = points[j][1]
	# 			if i is not j:
	# 				diam += distance(i_x, i_y, j_x, j_y)
	# 				if diam	> biggest_diameter:
	# 					biggest_diameter = diam			
	# 			j += 1
	# 		i += 1
	# 	return diameter

	def compute_tracker(self):
		print self.truck_id
		print type(self.truck_id)
		try:
			database = sqlite3.connect(self.db_path)
			cursor = database.cursor()
			print self.data
			table_query = "SELECT latitude, longitude, timestamp FROM master_table WHERE truck_id=?"
			result = cursor.execute((table_query, (self.truck_id)))			
			print "execute is working"
			self.data = cursor.fetchall()
			database.commit()
		except Exception as dbe:
			print "Something went wrong with the database in tracker.py"
			database.rollback()
			raise dbe
		finally:
			database.close()



		# calculate_stays()
		# calculate_trips()
		# calculate_warehouse()
		# calculate_paths()