#!/usr/bin/env python
import sys, csv, sqlite3



def main():
	for arg in sys.argv:
		print arg
	file_name = sys.argv[1]

	# Get the file to read from and the file to write to
	csv_write_from = str(file_name)
	csv_write_to = str(file_name).replace("raw_data", "processed_data")
	# table_name = csv_write_from.split("/")
	# table_name = table_name[-1]

	# Initialize database if not initialized with the master_table
	try:
		database = sqlite3.connect('./database/master.sqlite')
		cursor = database.cursor()
		create_table_SQL = "CREATE TABLE IF NOT EXISTS master_table (truck_id, latitude, longitude, timestamp)"
		cursor.execute(create_table_SQL)
		database.commit()
	except Exception as dbe:
		print "Something went wrong with the database creation"
		database.rollback()
		raise dbe
	finally:
		database.close()


	# Initialize variables to keep track of positions
	truck_identification_pos = -1
	latitude_identification_pos = -1
	longitude_identification_pos = -1
	date_pos = -1

	# Read from the csv file
	with open(csv_write_from, 'rU') as read_from, open(csv_write_to, 'wb') as write_to:
		is_set = False
		csv_reader = csv.reader(read_from, delimiter=',', quotechar = '|')
		csv_writer = csv.writer(write_to, delimiter=',', quotechar = '|', quoting=csv.QUOTE_MINIMAL)
		for row in csv_reader:
			print row
			# Defining the correct positions in the input CSV for the [truck_id, latitude, longitude, timestamp]
			if not is_set:
				arr = get_columns(row)
				# Set positions
				truck_identification_pos = arr[0]
				latitude_identification_pos = arr[1]
				longitude_identification_pos = arr[2]
				date_pos = arr[3]
				is_set = True
			# Conduct the writing to the filtered files and to the database
			else:
				data_arr = [row[truck_identification_pos], row[latitude_identification_pos], row[longitude_identification_pos], row[date_pos]]
				csv_writer.writerow(data_arr)
				try:
					database = sqlite3.connect('./database/master.sqlite')
					cursor = database.cursor()
					cursor.execute("INSERT INTO master_table VALUES (?, ?, ?, ?)", data_arr)
					database.commit()
				except Exception as e:
					print "Something went wrong inserting into the database"
					database.rollback()
					raise e
				finally:
					database.close()





## Returns an array with the positions in the csv: [truck_id, latitude, longitude, timestamp]
def get_columns(input_list):
	returned_positions = [-1, -1, -1, -1]

	# Initialize the possible headers to be compared against.
	#### NOTE: If your data has other header names, insert them into the relative set here
	id_name_set = set(['codigo', 'id', 'truck_id'])
	latitude_name_set = set(['latitud', 'latitude'])
	longitude_name_set = set(['longitud', 'longitude'])
	date_name_set = set(['fecha', 'date', 'timestamp'])

	# Iterating through the headers to set the right places 
	counter = 0
	for header in input_list:
		if header.lower() in id_name_set:
			returned_positions[0] = counter
		elif header.lower() in latitude_name_set:
			returned_positions[1] = counter
		elif header.lower() in longitude_name_set:
			returned_positions[2] = counter
		elif header.lower() in date_name_set:
			returned_positions[3] = counter
		counter += 1


	## Check to make sure the document is formatted right. If not we throw an exception
	for pos in returned_positions:
		if pos == -1:
			raise Exception("Input is improperly formatted. Check input formatting for the file: " + sys.argv[1])

	return returned_positions





if __name__=="__main__":
	main()