from ._hxml import VenturaXML
import ventura._hzip as hzip
import ventura._hweb as hweb
import ventura._hpath as hpath

__author__ = 'Hermes Passer'

def update_if_is_need(version, xml_url):
	# download and read xml
	xml_text = hweb.get_page(xml_url)
	
	ventura = VenturaXML(xml_text, version)
	if ventura.is_updated():
		return False
	
	hpath.delete_files(ventura.get_files_to_delete())
	hweb.download(ventura.get_link(), 'update.zip')
	hzip.extract('update.zip', '')
	
	return True
