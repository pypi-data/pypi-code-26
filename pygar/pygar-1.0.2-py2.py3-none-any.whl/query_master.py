#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from time import strptime

from pygar import config
from pygar.parser_dummy import parser_dummy
from pygar.query_csv import query_csv
from pygar.query_single_master import query_single_master


class query_master(query_csv):

	def __init__(self):
		super(query_master, self).__init__()

	def _map(self):
		return {
			'cik': 'CIK',
			'company': 'Company Name',
			'form': 'Form Type',
			'date_filed': 'Date Filed',
			'filename': 'Filename'
		}

	def _map_attr(self):
		return [('date', int), ('qtr', int), ('startqtr',int), ('endqtr',int)]

	def _qtr_valid(self, qtr):
		year_part = int(qtr[0:4])
		qtr_part = int(qtr[4:6])

		if year_part < 1993 or year_part > 2100 or qtr_part < 1 or qtr_part > 4:
			return None, None
		else:
			return year_part, qtr_part

	def _date_valid(self, date):
		try:
			strptime(date, '%Y%m%d')
			return True
		except ValueError:
			return False

	def _qtr_enum(self, startqtr, endqtr):
		ret = []
		startyr, startqn = self._qtr_valid(startqtr)
		endyr, endqn = self._qtr_valid(endqtr)

		if startyr is None or endyr is None:
			return None

		for yr in range(startyr, endyr+1):
			if yr == startyr:
				first_qtr = startqn
			else:
				first_qtr = 1

			if yr == endyr:
				last_qtr = endqn
			else:
				last_qtr = 4

			for qtr in range(first_qtr, last_qtr+1):
				ret.append((yr,qtr))

		return ret

	def _qtr_str(self, year_part, qtr_part):
		return "{:0>4}{:0>2}".format(year_part, qtr_part)

	# all logic done in execute(), nothing needed
	def _new_query(self):
		return parser_dummy()

	def execute(self):
		qtrs = None
		date = None

		if (
			self._attrs['startqtr'] is not None and
			self._attrs['endqtr'] is not None
		):
			qtrs = self._qtr_enum(
				self._attrs['startqtr'], self._attrs['endqtr']
			)

		elif self._attrs['qtr'] is not None:
			qtrs = [self._qtr_valid(self._attrs['qtr'])]

		elif self._attrs['date'] is not None:
			if self._date_valid(self._attrs['date']):
				date = self._attrs['date']

		if qtrs is None and date is None:
			return True, 'Could not determine master file(s) to retrieve.'

		if qtrs is not None:
			# download first before retrieval from files; this allows the
			# downloads to fail before loading a bunch of large data into memory
			master_objs = []
			for qtr in qtrs:
				str_qtr = self._qtr_str(qtr[0], qtr[1])

				sm = query_single_master()
				sm.set_attr('qtr', str_qtr)

				ret = sm.new_query()
				if not ret:
					return (True,
						'A quarter\'s master file could not be'
							' retrieved: {}'.format(str_qtr)
					)

				sm.filters = self._filters
				master_objs.append((sm, str_qtr))

			# now actually execute retrieval from downloaded objects
			ret = []
			for sm, str_qtr in master_objs:
				errbool, rows = sm.execute()

				if errbool is True:
					return True, rows

				if self._qp.field_names is None:
					self._qp.field_names = sm.field_names
					self._qp._field_names.append('Quarter')

				for row in rows:
					if row is False:
						return True, 'A master file could not be retrieved.'

					row.append(str_qtr)
					ret.append(row)

		else:
			sm = query_single_master()
			sm.set_attr('date', date)

			ret = sm.new_query()
			if not ret:
				return True, 'A master file could not be retrieved.'

			sm.filters = self._filters
			errbool, rows = sm.execute()

			if errbool is True:
				return True, rows

			self._qp.field_names = sm.field_names
			self._qp.field_names.extend(['Quarter', 'Date'])

			year, month, qtr = sm.date_parse()

			ret = []
			for row in rows:
				if row is False:
					return True, 'A master file could not be retrieved.'

				row.extend([qtr, date])
				ret.append(row)

		return False, ret
