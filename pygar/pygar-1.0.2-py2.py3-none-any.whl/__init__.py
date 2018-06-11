#
# pygaR
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: MIT
#

from pygar.query_form import query_form
from pygar.query_master import query_master
from pygar.query_scrape import query_scrape


class PygarException(Exception):
	"""
	Generic exception denoting it was thrown by pygaR
	"""
	pass


def _exec(command, **kwargs):
	cmd = command()

	# set attributes
	for attr,attr_type in cmd._map_attr():
		if attr in kwargs:
			cmd.set_attr(attr, kwargs[attr])
		elif attr_type is bool:
			cmd.set_attr(attr, False)
		else:
			cmd.set_attr(attr, None)

	# perform query
	ret = cmd.new_query()
	if not ret:
		raise PygarException('Query failed.')

	# gather args
	cmd_args = [i[0] for i in cmd._map_attr()] + \
		list(cmd._map_filters().keys())

	# split up filters/attributes
	for attr in cmd_args:
		if attr in kwargs:
			val = kwargs[attr]
			if attr in cmd._map_filters().keys():
				if val is not None:
					cmd.by(attr, str(val))
			else:
				for mapattr,attr_type in cmd._map_attr():
					if mapattr == attr:
						if type(val) is dict:
							cmd.set_attr(attr, val)
						else:
							cmd.set_attr(attr, attr_type(val))

						break

	# figure out mode
	if '_mode_tmp' in kwargs:
		cmd.mode = 'tmp'
	elif '_mode_file' in kwargs:
		cmd.mode = 'file'
	elif '_mode_dump' in kwargs:
		cmd.mode = 'dump'
	elif '_mode_data' in kwargs:
		cmd.mode = 'data'

	# execute and output
	errbool, ret = cmd.execute()
	if not errbool:
		return cmd.out(ret)
	else:
		raise PygarException(ret)

def form(path, **kwargs):
	"""
	Query a single form filing from the SEC EDGAR system.

	path -- The path of the EDGAR form starting with "edgar/"

	Returns a dictionary with two keys, "Header" and "Body", representing the
	contents of each.  Header contains the SEC filing header information.  Body
	contains a sequence of documents contained in the form.
	"""

	kwargs['path'] = path
	return _exec(query_form, **kwargs)

def master(**kwargs):
	"""
	Query a master file or sequence of master files from the SEC EDGAR system.

	Master files are indexes into the form filings provided.


	Three options are available for querying master data:

	Date: Specify a 'date' on the command line.

	Single Quarter: Specify a 'qtr' on the command line.

	Quarter Range: Specify both 'startqtr' and 'endqtr' on the command line.
	Quarters are then merged together.


	Options:

	date -- Specific date to query in format 20170504

	qtr -- Specific quarter to query in format 201702

	startqtr -- Beginning of a quarter range in format 201701

	endqtr -- Beginning of a quarter range in format 201702


	Filters:

	Filters can be passed as strings or as regular expressions.  If passed as a
	regular string, it is interpreted as an exact match.  If passed as a regula
	expression, the values of the specified field are compared to your regular
	expression expressed as '/COMPANYNAME/' or '@COMPANYNAME@'.  To specify case
	insensitivity, use '/cOmPaNyNaMe/i' or '@cOmPaNyNaMe@i'.

	cik -- A CIK is an SEC specific unique company identifier.

	company -- This searches for a company name.

	form -- Form filing type such as "4", "10-K", "10-Q", "DEF 14A"
	(there are hundreds of types, look at the EDGAR website for documentation)

	date_filed -- Date the form was filed.

	filename -- Filename in the EDGAR system.


	Returns a list.  First list item is a list of header names returned.
	Remaining list items are values of the returned rows.
	"""

	return _exec(query_master, **kwargs)

def search(**kwargs):
	"""
	Performs a query on either the header strings or the XML body of a sequence
	of filings, and flattens the result.


	Selection Options (see pygar.master's documentation for more information):

	date -- Specific date to query in format 20170504

	qtr -- Specific quarter to query in format 201702

	startqtr -- Beginning of a quarter range in format 201701

	endqtr -- Beginning of a quarter range in format 201702


	Search Options:

	header -- Boolean representing if to search the header information.
	Default false.

	query -- Dictionary representing the query to parse.  Query format and
	descriptions are described.


	Filters (see Filters section on pygar.master for more information), these
	filter the master files to scrape before digging into the forms and applying
	your query string:

	cik -- A CIK is an SEC specific unique company identifier.

	company -- This searches for a company name.

	form -- Form filing type such as "4", "10-K", "10-Q", "DEF 14A"
	(there are hundreds of types, look at the EDGAR website for documentation)

	date_filed -- Date the form was filed.

	filename -- Filename in the EDGAR system.


	Query Syntax:

	Queries are a way to prune and extract data from either the header or the
	XML root of the first XML document.  This will first prune the document
	based on your criteria, then extract the data.

	If you are parsing a dictionary or an XML document with the structure:

	{"root": [{"subelement": {"value": 17}}, {"subelement": {"value": 23}}]}

	With XML equivalent:

	<root><subelement><value>17</value></subelement><subelement><value>23</value></subelement></root>

	To retrieve these values you can use the following query:

	{"root": {"subelement": {"value": "elementValue"}}}

	Which will return a standard pygar.master() result set with each form
	queried with an additional header name "elementValue".  Because two results
	were returned, the row will be broken up into two rows as a result set with
	the first row containing 17 as the value of elementValue, and the second row
	containing 23.  Note that the "elementValue" text can be whatever you want
	to name this header field on output.

	To prune, specify the "_prune" keyword at the base of the element you wish
	to prune off.  For instance with the previous example:

	{"root": {"subelement": {"_prune": {"value": {"_lt": 23}}, "value": "elementValue"}}}

	Will return only one row, the elementValue of 17.  This uses the "_lt" (or
	less than) operator to prune any values off that are less than 23.

	All available pruning operators are as follows:

	_eq -- equal to operator

	_lt -- less than operator

	_gt -- greater than operator

	_le -- less than or equal operator

	_ge -- greater than or equal operator

	_z -- verifies value is an empty string

	_n -- verifies value is NOT an empty string


	Returns a list.  First list item is a list of header names returned.
	Remaining list items are values of the returned rows.
	"""

	return _exec(query_scrape, **kwargs)
