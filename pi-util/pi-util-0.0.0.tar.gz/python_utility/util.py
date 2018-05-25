# Purpose: Python Learning + Basic Utils 
# Author: Zeeshan
# Class: Util
class Util():

  info = "utility :v.0.0.0"
  @classmethod 
  def __init__(self):
    self.init = True
    
  @classmethod
  def is_empty(self, data):
     if self.is_string(data) or self.is_dictionary(data) or self.is_list(data):
      return self.is_shared_empty(data)
     else:
      return "unsupported_type"
    
  @classmethod
  def is_float(self, data):
     return isinstance(data, float)
    
  @classmethod
  def is_int(self, data):
     return isinstance(data, int)
    
  @classmethod
  def is_string(self, data):
     return isinstance(data, str)
    
  @classmethod
  def is_dictionary(self, data):
     return isinstance(data, dict)
    
  @classmethod
  def is_list(self, data):
     return isinstance(data, list)
    
  @classmethod
  def length(self, data):
     return len(data)

  @classmethod
  def is_shared_empty(self, data):
    if self.length(data) < 1:
      return True
    else:
      return False
