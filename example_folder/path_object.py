#!/usr/bin/env python
import sys, sqlite3, random
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

	############ STORAGE: storing values to SQLite Database ############
	## Used To Store All Stays to the Database in the 'stays' table
	def store_stays_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()


			stays_curs = cursor.execute("SELECT stay_count FROM stays WHERE carrier_ID=?", [str(self.truck_id)])
			stays_lst = set(stays_curs.fetchall())

			for stay in self.stay_set:
				rand_ID = int(random.random() * 100000)
				while True:
					if not rand_ID in stays_lst:
						stays_lst.add(rand_ID)
						break
					rand_ID = int(random.random() * 100000)
				lst = [str(self.truck_id), rand_ID, str(stay[0][0]), str(stay[0][1]), "", "", stay[2], stay[3]]
				for val in stay[1]:
					lst[4] = str(val[0])
					lst[5] = str(val[1])

					cursor.execute("INSERT INTO stays VALUES (?,?,?,?,?,?,?,?)", lst)

			database.commit()
			print "Stays entry done for: " + str(self.truck_id)
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()

	## Used To Store All Warehouses to the Database in the 'warehouses' table
	def store_warehouses_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			for warehouse in self.warehouses:
				cursor.execute("INSERT INTO warehouses VALUES (?, ?, ?)", [str(self.truck_id), warehouse[0], warehouse[1]])

			database.commit()
			print "Warehouse entry done for: " + str(self.truck_id)
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()

	## Used To Store All Trips to the Database in the 'trips' table
	def store_trips_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			trips_lst = cursor.execute("SELECT trip_count FROM trips WHERE carrier_ID=?", [str(self.truck_id)]).fetchall()
			count = 0
			if len(trips_lst) is not 0:
				count = max(trips_lst)[0] + 1

			for trip in self.trips:
				for med in trip:
					try:
						cursor.execute("INSERT INTO trips VALUES (?, ?, ?, ?)", [str(self.truck_id), count, med[0], med[1]])
					except IndexError as ie:
						print "weird one: " + str(med)
				count += 1	

			database.commit()
			print "Trips entry done for: " + str(self.truck_id)
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()

	## Used To Store All Destinations to the Database in the 'destinations' table
	def store_destinations_to_SQL(self, database_path):
		try:
			database = sqlite3.connect(database_path)
			database.text_factory = str
			cursor = database.cursor()

			dest_lst = cursor.execute("SELECT dest_count FROM destinations WHERE carrier_ID=?", [str(self.truck_id)]).fetchall()

			count = 0
			if len(dest_lst) is not 0:
				count = max(dest_lst)[0] + 1

			for dest in self.destinations:
				lst = [str(self.truck_id), count, str(dest[0][0]), str(dest[0][1]), "", ""]
				for val in dest[1]:
					lst[2] = str(val[0])
					lst[3] = str(val[1])
					cursor.execute("INSERT INTO destinations VALUES (?,?,?,?,?,?)", lst)
				count += 1

			database.commit()
			print "Destinations entry done for: " + str(self.truck_id)
		except Exception as dbe:
			database.rollback()
			raise dbe
		finally:
			database.close()








