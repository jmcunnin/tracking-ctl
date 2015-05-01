#!/usr/bin/env python
import sys, sqlite3
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
		self.destinations = list()

	############ MUTATORS: adding values to the fields ############
	def add_stay(self, stay, values, begin_time, end_time):
		tup = (stay, values, begin_time, end_time)
		self.stay_set.append(tup)

	def add_trip(self, points_list):
		self.trips.append(points_list)

	def add_warehouse(self, point):
		self.warehouses.append(point)

	def add_destination(self, dest, points_list):
		dest = (dest, points_list)
		self.destinations.append(dest)


	############ GETTERS: returning values from the fields ############
	def get_stays(self):
		return deepcopy(self.stay_set)

	def get_trips(self):
		return deepcopy(self.trips)

	def get_truckID(self):
		return self.truck_id

	def get_warehouse(self):
		return deepcopy(self.warehouses)

	def get_destinations(self):
		return deepcopy(self.destinations)

	#### Storing to SQL:
	def store_to_sql(self, database_path):
		store_stays_to_SQL(database_path)


	def store_stays_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			cursor.execute("CREATE TABLE IF NOT EXISTS  stays (identifier, count, stay_lat, stay_long, value_lat, value_long, begin_time, end_time )")
			stays_curs = cursor.execute("SELECT COUNT FROM stays WHERE identifier=?", [str(self.truck_id[0])])
			stays_lst = stays_curs.fetchall()
			
			count = 0
			if len(stays_lst) is not 0:
				count = max(stays_lst[0]) + 1

			for stay in self.stay_set:
				lst = [str(self.truck_id[0]), count, str(stay[0][0]), str(stay[0][1]), "", "", stay[2], stay[3]]
				for val in stay[1]:
					lst[4] = str(val[0])
					lst[5] = str(val[1])

					cursor.execute("INSERT INTO stays VALUES (?,?,?,?,?,?,?,?)", lst)
				count += 1

			print "stays done"
			database.commit()
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()


	def store_warehouses_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			cursor.execute("CREATE TABLE IF NOT EXISTS warehouses (related_truck, latitude, longitude)")
			for warehouse in self.warehouses:
				cursor.execute("INSERT INTO warehouses VALUES (?, ?, ?)", [str(self.truck_id[0]), warehouse[0], warehouse[1]])

			database.commit()
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()

	def store_trips_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()


			cursor.execute("CREATE TABLE IF NOT EXISTS trips (truck_id, count, value_lat, value_long)")
			trips_lst = cursor.execute("SELECT COUNT FROM trips WHERE truck_id=?", [str(self.truck_id[0])]).fetchall()
			count = 0
			if len(trips_lst) is not 0:
				count = max(trips_lst)[0] + 1

			for trip in self.trips:
				for med in trip:
					try:
						cursor.execute("INSERT INTO trips VALUES (?, ?, ?, ?)", [str(self.truck_id[0]), count, med[0], med[1]])
					except IndexError as ie:
						print "weird one: " + str(med)
				count += 1	

			database.commit()
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()


	def store_destinations_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			print "entering destination entry" 

			cursor.execute("CREATE TABLE IF NOT EXISTS destinations (truck_id, count, stay_lat, stay_long, value_lat, value_long)")
			dest_lst = cursor.execute("SELECT COUNT FROM destinations WHERE truck_id=?", [str(self.truck_id[0])]).fetchall()

			count = 0
			if len(dest_lst) is not 0:
				count = max(dest_lst)[0] + 1

			for dest in self.destinations:
				lst = [str(self.truck_id[0]), count, str(dest[0][0]), str(dest[0][1]), "", ""]
				for val in dest[1]:
					lst[2] = str(val[0])
					lst[3] = str(val[1])
					cursor.execute("INSERT INTO destinations VALUES (?,?,?,?,?,?)", lst)
				count += 1

			database.commit()
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()








