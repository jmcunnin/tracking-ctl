import unittest
from path_object import truck_path
from tracker import tracker



class TestTrackerMethods(unittest.TestCase):

	def setUp(self):
		self.database_path =  './database/master.sqlite'
		self.pathObject_201 = truck_path("11FC0201")
		self.test_tracker_201 = tracker(self.database_path, "11FC0201", self.pathObject_201, 100, 100, 100, 100, 100)

	
	# def test_path_object(self):
	# 	pathObject_201.get_truckID()
	def test_db_setup(self):
		self.test_tracker_201.compute_tracker()
		self.assertTrue(self.test_tracker_201.data)

		

	# def test_distance(self):

	# def test_medoid(self):

	# def test_diameter(self):

	# def test_calculate_stays(self):

	# def test_calculate_warehouse(self):



