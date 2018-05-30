import pkg_resources

ENCODING = 'utf-8'

LICENSE = ["APL-1.txt", 'Apache-2.txt', 'Artistic-2.txt', 'BSD+PATENT.txt', 'BSD-2.txt', 'BSD-3.txt',
			'CDDL-1.txt', 'ECL-2.txt', 'EPL-2.txt', 'GNU-2.txt', 'GNU-3.txt', 'IPA.txt',
			'ISC.txt', 'LGPL-2.txt', 'LGPL-2-1.txt', 'MIT.txt', 'MPL-2.txt', 'NASA-1.txt',
			'OFL-1.txt', 'OPL-2.txt', 'UCL-1.txt']

def get_license(index, author, year):
	global ENCODING
	global LICENSE

	year = bytes(str(year), ENCODING)
	author = bytes(author, ENCODING)

	recourse_package = __name__
	resource_path = '/'.join(('content', LICENSE[index - 1]))

	license = pkg_resources.resource_string(recourse_package, resource_path)
	license = license.replace(b'<YEAR>', year)

	if author:
		license = license.replace(b'<COPYRIGHT HOLDERS>', author)

	return license.decode(ENCODING)