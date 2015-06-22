#!/usr/bin/env python
import math as m


def filter(data, max_speed):
	ret_lst = [data[0]]
	max_speed = (float(max_speed)/(60.))*1000.
	print max_speed

	i = 0
	while i < (len(data) - 1):
		vel = velocity(data[i+1], data[i])
		if vel < max_speed:
			ret_lst.append([data[i+1]])
			i +=1
		else:
			print "jumped"
			i += 2
			ret_lst.append([data[i]])
	return ret_lst



def velocity(pt1, pt2):
	try:
		lat1, lon1, time1 = pt1
		lat2, lon2, time2 = pt2

		### Calculate d_t
		time1_arr = [int(time1[0:2]), int(time1[3:5]), int(time1[6:10]), int(time1[11:13]), int(time1[14:16]),
					 int(time1[17:19])]
		time2_arr = [int(time2[0:2]), int(time2[3:5]), int(time2[6:10]), int(time2[11:13]), int(time2[14:16]),
					 int(time2[17:19])]
		corrections = [1440., 43829., 525949., 60., 1, 1 / 60]

		d_t = sum([(t1 - t2) * corr for t1, t2, corr in zip(time1_arr, time2_arr, corrections)])


		### Calculate d_x
		earth_radius = 6367000
		lst = [pt1[0], pt1[1], pt2[0], pt2[1]]
		lat1, lon1, lat2, lon2 = map(m.radians, [float(x) for x in lst])

		a = m.sin((lat2 - lat1)/2)**2 + m.cos(lat1) * m.cos(lat2) * m.sin((lon2 - lon1)/2)**2
		c = 2 * m.asin(m.sqrt(a))
		d_x = earth_radius * c

		return d_x/d_t
	except ZeroDivisionError as ZDE:
		return 0
