import unittest
import mysql.connector as mysql
from models import Patient
import settings

import sys
sys.path.append("../")
from db2 import Session


class TestSession(unittest.TestCase):
	def setUp(self):
		self.session = Session(settings)
		self.session.connection.database = settings.DATABASE

	def tearDown(self):
		self.session.close()

	def test_MySQLConnection(self):
		with self.session as conn:
			self.assertIsInstance(conn, mysql.MySQLConnection)
			self.assertIsInstance(self.session.connection, mysql.MySQLConnection)
			self.assertIsInstance(conn.cursor(), mysql.cursor.MySQLCursor)

	def test_migrations(self):
		OK = self.session.makemigrations()
		self.assertEqual(OK, True)

	def test_database(self):
		self.assertEqual(self.session.connection.database, settings.DATABASE)

	def test_insert_query(self):
		patient = Patient(id=1, name='Abiira Nathan', 
		sex='Male', address='Uganda', mobile='0785434581', 
		next_of_kin = 'John K', religion='Protestant',
		marital_status='Married', date='1989-01-01 13:30:20')

		OK = self.session.add(patient)
		try:
			self.assertEqual(OK, True)
		except:
			self.assertIsInstance(OK, mysql.Error)

	def test_update_query(self):
		patient = Patient(id=1, name='Abiira Nathan', 
		sex='Male', address='Uganda', mobile='0785434581', 
		next_of_kin = 'John K', religion='Catholic',
		marital_status='Married', date='1989-01-01 13:30:20')

		OK = self.session.update(patient)
		try:
			self.assertEqual(OK, True)
		except:
			self.assertEqual(OK, False)

	def test_descriptors(self):
		with self.assertRaises(ValueError):
			patient = Patient(mobile='07894565434581')

		with self.assertRaises(TypeError):
			patient = Patient(id='Nathan')

		with self.assertRaises(TypeError):
			patient = Patient(name=1000)

		with self.assertRaises(ValueError):
			patient = Patient(name='Abiira Nathan of Uganda')


	def test_select_query(self):
		results = self.session.get(Patient)
		self.assertTrue(isinstance(results, list))

		results2 = self.session.get(Patient, returnDict=True)
		if results:
			self.assertTrue(isinstance(results2[0], dict))


	def test_settings(self):
		self.assertTrue(hasattr(settings, 'USER'))
		self.assertTrue(hasattr(settings, 'HOST'))
		self.assertTrue(hasattr(settings, 'DATABASE'))
		self.assertTrue(hasattr(settings, 'PASSWORD'))
		self.assertTrue(hasattr(settings, 'DEBUG'))

	def test_models(self):
		self.assertTrue(hasattr(Patient, '_fields'))
		self.assertTrue(hasattr(Patient, 'types'))
		
if __name__ == '__main__':
	unittest.main()