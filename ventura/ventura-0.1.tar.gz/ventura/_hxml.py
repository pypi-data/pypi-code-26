import xml.etree.ElementTree as ET
import os

class VenturaXML:
	def __init__(self, xml_text, program_version):
		self.root = ET.fromstring(xml_text)
		self.current_version = program_version
		self.get_last()
	
	def is_updated(self):
		return self.current_version >= self.last_version
	
	def	get_files_to_delete(self):
		return self.update_node.find('.//delete').text.split(',')
	
	def get_link(self):
		return self.update_node.find('.//url').text
	
	# Get newer update node and it version
	def get_last(self):		
		nodes = self.root.findall('.//update')		
		versions = {}
		for node in nodes:
			ver = node.attrib['version']
			versions[float(ver)] = node
					
		last = max(versions, key=float)
		self.last_version = last
		self.update_node = versions[last]
