#!/usr/bin/env python
import sys
import math as m

## Reforms the input data based upon the max speed allowable
class filter_noise:

	## Max speed is input in km/h
	def __init__(self, data, max_speed):
		self.data = data
		self.max_speed = self.convert_kph(max_speed)
		print self.max_speed

	def convert_kph(self, speed):
		return (float(speed)/(60.))*1000.

	def filter(self):
		i = 0
		while i < len(self.data)-1:
			try:
				j = i+1
				if self.data[i] is not None:
					delta_d = self.distance(self.data[j][1:2], self.data[i][1:2])
					delta_t = self.time_difference(self.data[j][2], self.data[i][2])
					if delta_d/delta_t > self.max_speed:
						self.data[j] = None
			except IndexError as ie:
				# print "overflowed"
				pass
		return [x for x in self.data if x is not None]



	def distance(self, pt1, pt2):
		earth_radius = 6371000.  ## Radius in meters
		pt1_x = earth_radius*m.cos(float(pt1[0]))*m.cos(float(pt1[1]))
		pt1_y = earth_radius*m.cos(float(pt1[0]))*m.sin(float(pt1[1]))
		pt1_z = earth_radius*m.sin(float(pt1[0]))

		pt2_x = earth_radius*m.cos(float(pt2[0]))*m.cos(float(pt2[1]))
		pt2_y = earth_radius*m.cos(float(pt2[0]))*m.sin(float(pt2[1]))
		pt2_z = earth_radius*m.sin(float(pt2[0]))

		return pow((pow((pt1_x - pt2_x), 2) + pow((pt1_y - pt2_y), 2) + pow((pt1_y - pt2_y), 2)), .5)


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
