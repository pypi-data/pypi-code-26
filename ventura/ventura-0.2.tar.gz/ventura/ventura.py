from ._hxml import VenturaXML
import ventura._hzip as hzip
import ventura._hweb as hweb
import ventura._hpath as hpath

__author__ = 'Hermes Passer'

def update_if_is_need(version, xml_url, path = ''):
	# download and read xml
	xml_text = hweb.get_page(xml_url)
	
	ventura = VenturaXML(xml_text, version)
	if ventura.is_updated():
		return False
	
	links = ventura.get_links()
	for link in links:
		path = path + '//' if path != '' else ''
		hweb.download(link, path + 'update.zip')
		hzip.extract(path + 'update.zip', path)
	
	hpath.delete_files(ventura.get_files_to_delete())
	return True
