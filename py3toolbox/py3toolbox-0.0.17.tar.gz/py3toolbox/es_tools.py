#!/usr/bin/python3 -W ignore
import os
import requests
import elasticsearch as es
import json
from elasticsearch import helpers
from elasticsearch_dsl import Search




class ES():
  def __init__(self, es_url):
    self.es_url  = es_url
    self.es_inst = es.Elasticsearch([self.es_url],scheme="https", verify_certs=False)
    self.indices = {}
    self.aliases = {}
    self.scanner = None
    self.batch_data = [] 
    self.get_es_info()
    self.scanner = None
  
  def _format_index_doc_id(self, index, doc_type,doc_id):
    return_str = '{0}|{1}|{2}'.format(index,doc_type,doc_id)
    return  return_str
    
  def _parse_index_doc_id(self, index_doc_id_str):
    m = re.match( r'^([^\|]+)\|([^\|]+)\|([^\|]+)$', index_doc_id_str, re.M|re.I)
    if m : return (m.group(1),m.group(2),m.group(3))
    else : return None   
    
  def get_es_info(self):
    self.indices  = { index_name: self.es_inst.indices.get('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get('*').keys()) if not x.startswith('.') ]}
    self.aliases  = { index_name: self.es_inst.indices.get_alias('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get_alias('*').keys()) if not x.startswith('.') ]}
    pass

  def get_index_by_alias(self, alias):
    result = []
    for k,v in self.aliases.items() :
      if alias in v['aliases']:
        result.append(k)
    if len(result) > 0: return  result[0]
    return None

  def set_alias(self, index, alias) :
    if self.es_inst.indices.exists_alias(name=alias):
      self.es_inst.indices.delete_alias(index = "*", name=alias)
    self.es_inst.indices.put_alias(index=index,      name=alias)       
    
  def get_doc_count(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    return int(self.es_inst.count(index=index)['count'])

  def get_ids(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    self.index_type_ids = []
    self.id_scanner = es.helpers.scan(self.es_inst, index=index, query={"stored_fields": ["_id"], "query": {"match_all": {}}})
    print (self.id_scanner)
    for doc in self.id_scanner :
      self.index_type_ids.append(self._format_index_doc_id(index,  doc['_type'] ,  doc['_id']))
    return (self.index_type_ids)
    
  def get_doc_by_id(self, doc_type, doc_id, index=None, alias=None) :
    if index is None: index = self.get_index_by_alias(alias=alias)
    doc = self.es_inst.search(index=index, doc_type=doc_type, body={"query": {"match": {"_id": doc_id}}})
    if int(doc['hits']['total']) == 0 : return None
    return (doc['hits']['hits'][0]['_source'])

  def bulk_exec(self, batch):
    helpers.bulk(self.es_inst, batch, request_timeout=120)
    
  def create_index(self, index, mapping_json):
    self.es_inst.indices.create(index=index, body=mapping_json)
    self.get_es_info()
  
  def delete_index(self, index):
    self.es_inst.indices.delete(index=index, ignore=[400, 404])
    self.get_es_info()

  def get_analyzer(self,index=None, alias=None):
    mapping_dic = self.get_mapping(json_fmt=False, index=index, alias=alias)
    analyzers    = mapping_dic['settings']['index']['analysis']['analyzer'].keys()
    return analyzers
    
  def get_mapping(self, json_fmt=True, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    mapping_dic = self.indices[index]
    if json_fmt :   mapping = json.dumps(mapping_dic, sort_keys=True, indent=2)
    else        :   mapping = mapping_dic
    return mapping

  def test_analyzer(self, index=None, alias=None, analyzer=None, text=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    url = self.es_url + '/' + alias + '/_analyze'
    headers = {"Accept": "application/json"}
    body_data = '{"analyzer": "' + analyzer + '", "text":    "' + text + '" }'    
    response = requests.get(url,data = body_data)
    return (response.text)

  def query_by_dsl(self, doc_type, dsl_json, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    result = []
    result_page = self.es_inst.search(index=index, doc_type=doc_type, scroll = '5m', size=1000, body=dsl_json)
    scroll_id = result_page['_scroll_id']
    scroll_size = result_page['hits']['total']
    while (scroll_size > 0):
      result.extend(result_page['hits']['hits'])
      result_page = self.es_inst.scroll(scroll_id = scroll_id, scroll = '2m')
      scroll_id = result_page['_scroll_id']
      scroll_size = len(result_page['hits']['hits'])
    return (result)       

  def init_index_scanner(self, index=None, alias=None, dsl_json=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    if dsl_json is None: # assume all records
      dsl_json = {"query": {"match_all": {}}}
    self.scanner = es.helpers.scan(self.es_inst, index=index, query=dsl_json)
  
  
    
if __name__ == "__main__": 

  es1 = ES('https://search-tafe-search-dev-3jv2rifl7znw4hss5mmkq3occa.ap-southeast-2.es.amazonaws.com')
  #print (es1.indices)
  #print (es1.aliases)
  #print (es1.get_index_by_alias('offerings'))
  #print (es1.get_doc_count(alias='offerings')) 
  
  dsl_json =  {
        "_source" : ["learning_product.product_identifier"],
        "query": {
          "regexp": {
              "learning_product.product_identifier.keyword": "BSB50215.*" 
          }
      }
  }
  #print (es1.get_analyzer(alias='products'))
  result = es1.query_by_dsl('detail', dsl_json=dsl_json, alias='offerings')
  print (len(result))
  #print (result)
  
  print (es1.get_ids('products'))
  #print (es1.get_doc_by_id(doc_type='detail', doc_id= 'UOS-SIT40212-15OTE-059' , alias='offerings')) 
 
  pass  