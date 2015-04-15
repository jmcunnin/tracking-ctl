#!/usr/bin/env python
import sys, sqlite3, math

from path_object import truck_path

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
		self.min_stay_time = min_stay_time
		self.min_warehouse_time = min_warehouse_time
		self.max_idle_time = max_idle_time
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

				self.path.add_stay(self.medoid(curr_list), self.data[i:j], self.data[i][2], self.data[j][2])
				i = j + 1




	def calculate_trips(self):
		## Calculate our trips here and add to the path_object
		stays = self.path.get_stays()
		
		if len(stays) == 0:
			raise RuntimeError("No stays calculated. Reprametrize")

		## Add a trip object if the first stay does not occur until after the start of the data
		if self.time_difference(stays[0][2], self.data[0][2]) > 0:
			start_time = self.data[0][2]
			j = 0
			while(self.time_difference(stays[0][2], self.data[j][2]) != 0) and j < len(self.data):
				j += 1
			self.path.add_trip(start_time, self.data[j][2], self.data[0:j])
		
		## Add all of the other stays
		data_pointer = 0
		i = 0
		while i < len(stays)-1:
			end_first = stays[i][3]
			begin_second = stays[i+1][2]
			while self.time_difference(self.data_pointer, end_first) < 0:
				data_pointer += 1
			start_trip = data_pointer
			while self.time_difference(begin_second, self.data[data_pointer][2]) < 0:
				data_pointer += 1
			self.path.add_trip(self.data[start_trip][2], self.data[data_pointer][2], self.data[i:j])

		if self.time_difference(self.data[-1][2], stays[-1][3]) > 0:
			y = -1
			while self.time_difference(self.data[y][2], stays[-1][3]) > 0:
				y -= 1
			start_pt = len(self.data) + y -1
			self.path.add_trip(self.data[start_pt][2], self.data[-1][2], self.data[start_pt:])


	def calculate_paths(self):
		## Calculate our paths, store as a trace object and add to the path_object	
		stays = self.path.get_stays()
		warehouses = self.path.get_warehouse()


		new_list = []
		while stays:
			new_point = stays.pop(0)
			if self.stay_contains_warehouse(new_point, warehouses):
				self.path.add_path(new_list.append(new_point))
				new_list = [new_point]
			else:
				new_list.append(new_point)

		if len(new_list) > 0:
			self.path.add_path(new_list)




	
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


	## Computes the distance between the x and y coordinates passed 
	def distance(self, pt1, pt2):

		delta_x = float(pt1[0])-float(pt2[0])
		delta_y = float(pt1[1])-float(pt2[1])
		return pow(pow(delta_x, 2) + pow(delta_y, 2), .5)

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
			cursor = database.cursor()
			table_query = 'SELECT latitude, longitude, timestamp FROM master_table WHERE truck_id=?'
			result = cursor.execute(table_query, [str(self.truck_id)])		
			self.data = cursor.fetchall()
			database.commit()
		except Exception as dbe:
			print "Something went wrong with the database in tracker.py"
			database.rollback()
			raise dbe
		finally:
			database.close()

		self.calculate_stays()
		self.calculate_trips()
		self.calculate_warehouse()
		self.calculate_paths()




