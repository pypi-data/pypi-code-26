import xml.etree.ElementTree as et


def is_xml(xml_text) :
  try :
    x = et.fromstring(xml_text)
    return True
  except Exception as e:
    return False  


def pretty_xml(xml_file) :
  xml_doc = et.parse(xml_file)
  return (et.tostring(xml_doc, pretty_print=True).decode("utf-8")) 
  
  
def parse_xml(xml_text) :
  try :
    xml_obj = et.fromstring(xml_text)
    return xml_obj
  except Exception as e:
    return None  

  
def get_xml_element(xml_obj,xpath):
  xml_element = None
  xml_element = xml_obj.find(xpath)
  if xml_element is not None : 
    return xml_element.text
  else :
    return ""

  
if __name__ == "__main__":
  #xml = parse_xml(read_file('C:/TEMP/offering.xml'))
  #print (xml)
  #print (get_xml_element(xml, "./LearningProductOrganisationOffering/LearningProductOrganisationOffering-LearningProductOrganisationOfferingRelationshipList/LearningProductOrganisationOffering-LearningProductOrganisationOfferingRelationship/LearningProductOrganisationOfferingTo/LearningProduct/"))
  pass    