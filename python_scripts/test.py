#!/usr/bin/env python
import sys, sqlite3, math

from path_object import truck_path
from copy import deepcopy

try:
	database = sqlite3.connect('./database/master.sqlite')
	database.text_factory = str
	cursor = database.cursor()
	table_query = 'SELECT latitude, longitude, timestamp FROM master_table WHERE truck_id=?'
	result = cursor.execute(table_query, ["11FC0202"])		
	# self.data = cursor.fetchall()
	print cursor.fetchone()
except Exception as e:
	database.rollback()
	raise e
finally:
	database.close()