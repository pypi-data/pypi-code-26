import time
import datetime
import maya
import pytz

def get_timestamp(ts_format='%Y-%m-%d %H:%M:%S', iso_format=False) :
  if iso_format == False: 
    return '{:{ts_fmt}}'.format(datetime.datetime.now(), ts_fmt = ts_format)
  if iso_format == True: 
    return datetime.datetime.now().isoformat()   

  
def timer_start():
  start = time.time()
  return (start)  
  
def timer_check(start):
  return(time.time() - start)   

  
def get_epoch(self,time_string):
  dt = maya.when(time_string)
  return  dt.epoch

def cal_days_diff(dt_str1, dt_str2, ts_fmt = '%Y-%m-%d %H:%M:%S'):
  dt1 = datetime.datetime.strptime(dt_str1, ts_fmt)
  dt2 = datetime.datetime.strptime(dt_str2, ts_fmt)
  diff   = dt2 - dt1
  return diff.days
  
  
if __name__ == "__main__":
  print (get_timestamp(iso_format=True))
  pass