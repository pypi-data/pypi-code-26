#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from pygar import config
from pygar.cache import cache
from pygar.parser_index import parser_index_sep
from pygar.query_csv import query_csv


class query_single_master(query_csv):
	_path = None

	def __init__(self):
		super(query_single_master, self).__init__()

	def _map(self):
		return {
			'cik': 'CIK',
			'company': 'Company Name',
			'form': 'Form Type',
			'date_filed': 'Date Filed',
			'filename': 'Filename'
		}

	def _map_attr(self):
		return [('date', int), ('qtr', int)]

	def date_parse(self):
		year = int(self._attrs['date'][0:4])
		month = int(self._attrs['date'][5:6])

		if month in (1,2,3):
			qtr = 1
		elif month in (4,5,6):
			qtr = 2
		elif month in (7,8,9):
			qtr = 3
		elif month in (10,11,12):
			qtr = 4

		return year, month, qtr

	def _new_query(self):
		if 'filename' in self._attrs and self._attrs['filename'] is not None:
			errbool, ret = cache.get(self._attrs['filename'])

		elif 'qtr' in self._attrs and self._attrs['qtr'] is not None:
			year = int(self._attrs['qtr'][0:4])
			qtr = int(self._attrs['qtr'][5:6])
			self._path = 'edgar/full-index/{}/QTR{}/master.gz'.format(
				year, qtr
			)
			errbool, ret = cache.get(self._path, qtr=(year, qtr), expires=True)

		elif 'date' in self._attrs and self._attrs['date'] is not None:
			year, month, qtr = self.date_parse()

			self._path = 'edgar/daily-index/{}/QTR{}/master.{}.idx'.format(
				year, qtr, self._attrs['date']
			)
			errbool, ret = cache.get(
				self._path, date=self._attrs['date'], expires=True
			)

		else:
			self._path = config.START_PATH
			errbool, ret = cache.get(self._path, expires=True)

		if errbool:
			return False

		parser = parser_index_sep('|')
		parser.open(cache.full_fs_path(self._path))
		return parser
