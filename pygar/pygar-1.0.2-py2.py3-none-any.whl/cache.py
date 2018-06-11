#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from time import mktime, strptime
import certifi, curl, os, sys

from pygar import config


class _cache(object):

	def __init__(self):
		pass

	def full_fs_path(self, path, splitter=False):
		if splitter is False:
			ret = str(os.path.join(config.CACHE_PATH, path))

		else:
			paths = [config.CACHE_PATH]
			paths.extend(path.split(splitter))
			ret = str(os.path.join(*paths))

		return ret

	def full_url_path(self, path):
		return '{}/{}'.format(config.EDGAR_BASE, path)

	# does equivalent of "mkdir -p" in UNIX (creates all intermediate dirs)
	def mkdir_p(self, path):
		path_work = path
		paths_to_make = []

		while not os.path.exists(path_work):
			paths_to_make.append(path_work)
			path_work = os.path.dirname(path_work)

		paths_to_make.reverse()

		while len(paths_to_make) != 0:
			os.mkdir(paths_to_make.pop(0))

	def _get_remote_timestamp(self, simple_path):
		index_simple_path = '{}/{}'.format(
			os.path.dirname(simple_path), 'index.html'
		)

		if not self.get(index_simple_path, expires=True, doprint=False):
			return False

		full_index_path = self.full_fs_path(index_simple_path, splitter='/')
		base_simple_path = os.path.basename(simple_path)

		f = open(full_index_path, 'r')
		lines = f.readlines()
		f.close()
		for line in lines:
			if line.find(base_simple_path) != -1:
				timestr_tags = line[line.rfind('<td>'):]
				timestr = timestr_tags[4:26]
				timestamp = mktime(strptime(timestr, '%m/%d/%Y %I:%M:%S %p'))
				return timestamp

		return False

	def _get(self, simple_path,
		date=False, qtr=False, expires=False, doprint=True
	):
		full_fs_path = self.full_fs_path(simple_path, splitter='/')
		full_url_path = self.full_url_path(simple_path)

		# test expiration of the file (always expire index.html files)
		if (
			os.path.exists(full_fs_path) and
			os.path.basename(simple_path) != 'index.html'
		):
			# regular file, don't test for expiration
			if not expires:
				return False, None

			# qtr file or date file that can expire
			filesystem_timestamp = os.path.getmtime(full_fs_path)
			cutoff_timestamp = self._get_remote_timestamp(simple_path)
	
			# scrape method didn't work for timestamp, use fallback method
			if not cutoff_timestamp:
				sys.stderr.write(
					'Using fallback caching check for [{}]\n'.format(
						simple_path
					)
				)

				if qtr is not False and type(qtr) is tuple:
					year, qtr = qtr
					month = (qtr*3) + 1
					if month == 13:
						month = 1
						year += 1

					st = strptime(
						'{}{}01 23:59:59'.format(year, month),
						'%Y%m%d %H:%M:%S'
					)
					cutoff_timestamp = mktime(st)

				elif date is not False:
					st = strptime('{} 23:59:59'.format(date), '%Y%m%d %H:%M:%S')
					cutoff_timestamp = mktime(st)

				# nothing passed in, just cause the comparison to fail and force
				# a file download
				else:
					cutoff_timestamp = filesystem_timestamp

			# do comparison to see if the expiration cutoff has been reached
			if cutoff_timestamp < filesystem_timestamp:
				return False, None

		try:
			if doprint:
				sys.stderr.write('Downloading: [{}]... '.format(simple_path))
				sys.stderr.flush()

			self.mkdir_p(os.path.dirname(full_fs_path))

			c = curl.Curl(full_url_path)
			c.set_option(curl.pycurl.CAINFO, certifi.where())
			c.set_option(curl.pycurl.TIMEOUT, config.CACHE_TIMEOUT)
			data = c.get()

			f = open(full_fs_path, 'wb')
			f.write(data)
			f.close()

			if doprint: sys.stderr.write('done\n')
			errbool = False
			error = None

		except curl.pycurl.error as e:
			errbool = True
			error = e
		except KeyboardInterrupt:
			errbool = True
			error = 'Keyboard Interrupt'
		except Exception as e:
			errbool = True
			error = e

		# if download interrupted, remove created file otherwise we have a
		# partial file downloaded
		if errbool:
			if os.path.exists(full_fs_path):
				os.unlink(full_fs_path)

			if doprint: sys.stderr.write('ERROR\n')

		return errbool, error

	def get(self, simple_path,
		date=False, qtr=False, expires=False, doprint=True
	):
		for i in range(0, config.CACHE_RETRIES):
			errbool, ret = self._get(simple_path, date, qtr, expires, doprint)
			if not errbool:
				break

		return errbool, ret

cache = _cache()
