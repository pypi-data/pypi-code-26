from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import random
import datetime
import os

debug_data = {
"RESULT":"",
"STATE":"CT",
"STATE FULL":"Connecticut",
"BIRTH DATE":"1956 3 18",
"FIRST NAME":"MARK",
"LAST NAME":"WISLAND",
"SEX":"BOY",
"ZIP":"53204",
"EMAIL":"mcwisland@gmail.com",
"SSN":"397548208",
"ADDRESS":"825 S.14TH ST",
"CITY":"MILWAUKEEMILWAUKEE",
"HOME PHONE":"4145514925",
"WORK PHONE":"5104907911",
"BANK NAME":"bank of america",
"ROUTING NUM":"122000661",
"ACCOUNT NUM":"2152876854",
"LOAN AMOUNT":"1500",
"JOB TITLE":"service coordinator",
"EMPLOYER NAME":"los angeles county",
"EMPLOYER TIME":"24",
"RENT OWN":"RENT",
"DRIVER LISTEN":"w2455435609806",
"CONTACT TIME":"MORNING",
"PAY FRE":"BIWEEKLY",
"RESIDENCE LENGTH":"3",
"INCOME":"5500",
"MORTGAGE":"150000",
"PROPERTY":"150000",
"CARD NUM":"4658581608177115",
"CARD NAME":"BARBARA J SAYLOR",
"PAY SOURCE":"e",
"CARD NUM":"4658581608177115",
"CVV":"568"
}

debug_data_p = dict({"MONTH":"12","YEAR":"1992","DAY":"12","0_MONTH":"12","0_DAY":"12","APT":"APT 12"},**debug_data)

class InsertFormBase:
  def open_url(self,token,user_agent=None,driver=None):
    driver = os.path.join(os.path.dirname(__file__),'geckodriver.exe')
    if not user_agent:
      if not driver:
        self.driver = webdriver.Firefox()
      else:
        self.driver = webdriver.Firefox(executable_path = driver)
    else:
      profile = webdriver.FirefoxProfile() 
      profile.set_preference("general.useragent.override",user_agent)
      if driver:
        self.driver = webdriver.Firefox(profile,executable_path = driver)
      else:
        self.driver = webdriver.Firefox(profile)
        
    if not token.startswith("http"):token = "http://" + token
    try:self.driver.get(token)
    except:return False

    try:
      self.driver.maximize_window()
      #self.driver.minimize_window()
    except:pass
    return True

  def insert(self,d):raise NameError("no methods")


  def my_click_mark(self,time = 40,**kwargs):
    winsound.PlaySound('SystemExit',flags=winsound.SND_ALIAS)
    input("[-] 请输入验证码后回车.")
    _t = list(kwargs.items())[0]
    exec("self.driver.find_element_by_%s(\"%s\").click()"%(_t[0],_t[1]))
    time.sleep(time)

    
  ## random_p([1,3,4],[0.2,0.3,0.5])
  def random_p(self,_list, p):
    x = random.uniform(0,1)
    cu = 0.0
    for r, i in zip(_list, p):
      cu += i
      if x < cu:return r

  def my_click(self,start=0,end=0,**kwargs):
    _t = list(kwargs.items())[0]
    time.sleep(start)
    exec("self.driver.find_element_by_%s(\"%s\").click()"%(_t[0],_t[1]))
    time.sleep(end)

  def my_slide(self,value=(0,0),id=None,name=None,xpath=None):
    value = list(value)
    if id     :e = self.driver.find_element_by_id(id)
    elif name :e = self.driver.find_element_by_name(name)
    elif xpath:e = self.driver.find_element_by_xpath(xpath)
    ActionChains(self.driver).click_and_hold(e).move_by_offset(value[0],value[1]).release(e).perform()

  def my_save_mark(self,mark="mark.png",html_img="page.png",id=None,name=None,xpath=None):
    if id     :e = self.driver.find_element_by_id(id)
    elif name :e = self.driver.find_element_by_name(name)
    elif xpath:e = self.driver.find_element_by_xpath(xpath)
    self.driver.save_screenshot(html_img)
    im = Image.open(html_img).crop((int(e.location['x']),int(e.location['y']),int(e.location['x'] + e.size['width']),int(e.location['y'] + e.size['height'])))
    im.save(mark)
    os.remove(html_img)
        
  def my_send(self,value="",**kwargs):
    _t = list(kwargs.items())[0]
    if isinstance(value,list):
      for i in value:
        exec("self.driver.find_element_by_%s(i[1]).clear()"%i[0])
        exec("self.driver.find_element_by_%s(i[1]).send_keys(i[2])"%i[0])         
    exec("self.driver.find_element_by_%s(\"%s\").clear()"%(_t[0],_t[1]))
    exec("self.driver.find_element_by_%s(\"%s\").send_keys(value)"%(_t[0],_t[1]))
    

  def my_wait_click(self,end=5,timeout=80,**kwargs):
    _t = list(kwargs.items())[0]
    try:
      exec("WebDriverWait(self.driver,%d).until(EC.presence_of_element_located((By.%s,\"%s\")))"%(timeout,_t[0].upper(),_t[1]))
      time.sleep(end)
      return True
    except:
      return False

  def wait_title_is_not(self,title):
    try:
      WebDriverWait(self.driver,120).until_not(EC.title_is(title))
      return True
    except:return False


  def my_state(self,value=0,id=None,name=None,xpath=None):
    if id     :e = self.driver.find_element_by_id(id)
    elif name :e = self.driver.find_element_by_name(name)
    elif xpath:e = self.driver.find_element_by_xpath(xpath)

    try:
      Select(e).select_by_visible_text(self.d["STATE"].upper())
      return
    except:pass
    
    try:
      Select(e).select_by_visible_text(self.d["STATE"].lower())
      return
    except:pass
    
    try:  
      Select(e).select_by_visible_text(self.d["STATE FULL"])
      return
    except:pass
    Select(e).select_by_index(random.randint(1,10))
        
    
  def my_select(self,value=0,id=None,name=None,xpath=None):
    if id     :e = self.driver.find_element_by_id(id)
    elif name :e = self.driver.find_element_by_name(name)
    elif xpath:e = self.driver.find_element_by_xpath(xpath)
        
    if   isinstance(value,int):Select(e).select_by_index(value)
    elif isinstance(value,str):Select(e).select_by_visible_text(value)
    elif isinstance(value,list):Select(e).select_by_index(random.randint(value[0],value[1]))


  def is_element_present(self, how, what):
    try: self.driver.find_element(by=how, value=what)
    except NoSuchElementException as e: return False
    return True
