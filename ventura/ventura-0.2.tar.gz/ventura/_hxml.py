import xml.etree.ElementTree as ET
import operator
import os

class UpdateNode:
	def __init__(self, version, node):
		self.node = node
		self.version = version

class VenturaXML:
	def __init__(self, xml_text, program_version):
		self.root = ET.fromstring(xml_text)
		self.current_version = program_version
		self.get_latest()
	
	def is_updated(self):
		return self.current_version >= self.last_version
			
	def	get_files_to_delete(self):
		all_files = []
		for update_node in self.update_nodes:
			if (update_node != None):
				del_txt = update_node.node.find('.//delete').text
				all_files += del_txt.split(',') if del_txt != None else ''
				
		return all_files
	
	def get_links(self):
		links = []
		for update_node in self.update_nodes:
			if (update_node != None):
				link = update_node.node.find('.//url').text
				links.append(link) if link != None else ''
		
		return links
	
	# Get newer update nodes and it versions
	def get_latest(self):		
		nodes = self.root.findall('.//update')		
		versions = []
		for node in nodes:
			ver = float(node.attrib['version'])
			if (ver > self.current_version):
				versions.append(UpdateNode(ver, node))
		
		if (versions == []):
			self.last_version = self.current_version
			self.update_nodes = None
			return
		
		# sort value
		versions = sorted(versions, key = operator.attrgetter('version'))
		self.last_version = versions[len(versions) - 1].version
		self.update_nodes = versions

