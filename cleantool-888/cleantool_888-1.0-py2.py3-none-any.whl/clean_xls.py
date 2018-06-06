import pandas
import os
import xlrd
import random
import openpyxl
import re
import sys
from. import datas


class CleanXls:
    def __init__(self,head,path_old,path_new=None):
        self.path_old = path_old   #待整理表格文件 *.xlsx 完整路径
        self.path_new = path_new   #整理后新的表格文件生成路径
        self.head = head           #待整理表格 表头排列字典 {"FIRST NAME":2,....}表示FIRST NAME在旧表格的第二列
        self.head_new = list(datas.debug_data.keys())  #设定好的新表头列表
        self.datas = {}

    def get_data_form_txt(self,path):
      with open(path,"r")as f:
        return [i.strip() for i in f.readlines() if i.strip()]

    def main(self):
        s = os.listdir(os.path.join(sys.path[0],"data"))
        for i in s:
          self.datas[os.path.splitext(i)[0]] = self.get_data_form_txt(os.path.join(sys.path[0],"data",i))
        if not self.path_new:
            self.path_new =os.path.join(os.path.dirname(__file__),"new-"+os.path.basename(self.path_old))

        #获取待整理表格的旧表头列表
        old_head = xlrd.open_workbook(self.path_old).sheet_by_index(0).row_values(0)
        xls_head = []
        
        for i in self.head_new:
            try:
                xls_head.append(old_head[self.head[i]-1])
            except:
                xls_head.append(i)
    
        self.df = pandas.read_excel(self.path_old) #打开旧表格
        self.df.to_excel(self.path_new,columns=xls_head,index=False) #将旧表格列顺序重排
        wb=openpyxl.load_workbook(self.path_new) #将新表格表头改为new_head
        ws = wb.active
        for i in self.head_new:ws.cell(row=1,column=self.head_new.index(i)+1).value = i
        wb.save(self.path_new)
        
        self.clean()

      
    def clean(self):
        self.df = pandas.read_excel(self.path_new)
        df = self.df
        clean_data_list = ["CITY","ADDRESS","SEX","JOB TITLE",
                    "SSN","ROUTING NUM","ZIP","HOME PHONE","WORK PHONE",
                    "PAY FRE","CONTACT TIME","BIRTH DATE","CITY",
                     "DRIVER LISTEN","EMPLOYER NAME","BANK NAME","CVV",
                        "CARD NUM","EXPIRE","LAST NAME","ACCOUNT NUM"]
        for i in clean_data_list:
            if i in self.head:
                src = df[i]
            else:
                src = ["" for i in list(df["HOME PHONE"])]
            df[i] = list(map(getattr(self,"clean_"+i.replace(" ","_").lower()),src))
            
        if "STATE"not in self.head:df["STATE"] = list(map(self.state,df["STATE FULL"]))
        else:df["STATE FULL"] = list(map(self.state,df["STATE"]))

        #生成新表格
        df.to_excel(self.path_new,index=False)
    #根据名字判断性别

    def clean_last_name(self,value):
      if "-" in value:
        return value.split("-")[1]
      return value

    def clean_account_num(self,value):
      value = re.sub(r'\D', "", str(value))
      try:
        if len(value) < 4:return self.datas["account_num"].pop()
      except:return value
      return value
      
    def clean_expire(self,value):
      try:
        return "%d %s"%(value.month,str(value.year)[-2:])
      except:pass
      
      value = str(value)
      if (not value or (value == "nan")):return value
      s = [i for i in [re.sub(r'\D', "", i) for i in value.split("/")] if i]
      
      if len(s)==1:
          year = s[0][-2:]
          month = str(int(s[0][:-2]))

      elif len(s)==2:
          year = s[-1]
          month = str(int(s[-2]))
          if len(year)==4:year = year[-2:]
      return month + " " + year
      

    def clean_cvv(self,value):
      value = re.sub(r'\D', "", str(value))
      return value

    def clean_card_num(self,value):
      value = re.sub(r'\D', "", str(value))
      return value
    
    #ok
    def clean_driver_listen(self,value):
      value = str(value)
      if (not value or (value == "nan")) and self.datas["driver_listen"]:
        try:
          return self.datas["driver_listen"].pop()
        except:return value
      return value

    def clean_employer_name(self,value):
      value = str(value)
      if (not value or (value == "nan")) and self.datas["employer_name"]:
        try:
          return self.datas["employer_name"].pop()
        except:return value
      return value

    def clean_bank_name(self,value):
      value = str(value)
      if (not value or (value == "nan")) and self.datas["bank_name"]:
        try:
          return self.datas["bank_name"].pop()
        except:return value
      return value

    def clean_address(self,value):
      value = str(value)
      if (not value or (value == "nan")) and self.datas["address"]:
        try:
          return self.datas["address"].pop()
        except:return value
      return value
    #ok
    def clean_city(self,value):
      value = str(value)
      if (not value or (value == "nan")) and self.datas["city"]:
        try:
          return self.datas["city"].pop()
        except:return value
      return value
    
    #ok
    def clean_routing_num(self,value):
      value = re.sub(r'\D', "", str(value)) 
      if re.search("^\d{9}$",value):return value
      if re.search("^\d{8}$",value):return "0" + value
      try:
        return self.datas["routing_num"].pop()
      except:return value
    #ok
    def clean_home_phone(self,value):
      value = re.sub(r'\D', "", str(value))  #去除非数字字符
      return value

    #no
    def clean_work_phone(self,value):
      value = re.sub(r'\D', "", str(value))
      if len(value) == 10:return value
      #非10位的电话处理
      return value

    #bug
    def clean_sex(self,value):
      value = str(value)
      if not value or (value == "nan"):
        if value.capitalize() in datas.boy_names:return "BOY"
        if value.capitalize() in datas.girl_names:return "GIRL"
        return random.choice(["BOY","GIRL"])
      return value
    
    #ok
    def clean_job_title(self,value):
      value = str(value)
      if not value or (value == "nan"):
        return random.choice(datas.job_title)
      return value
    #ok
    def clean_zip(self,value):
      value = re.sub(r'\D', "", str(value))
      if re.search("^\d{5}$",value):return value
      if re.search("^\d{4}$",value):return "0" + value
      try:
        return self.datas["zip"].pop()
      except:return value

    #ok
    def clean_email(self,value):
      value = str(value)
      if not value or (value == "nan"):return self.datas["email"].pop().lower()
      if ("@" in value) and ("." in value):return value.lower()
      try:
        return self.datas["email"].pop().lower()
      except:return value

    #ok
    def clean_ssn(self,value):
      value = re.sub(r'\D', "", str(value)) 
      if re.search("^\d{9}$",value):return value
      if re.search("^\d{8}$",value):return "0" + value
      try:
        return self.datas["ssn"].pop()
      except:return value
      
    #ok
    def clean_contact_time(self,value):
        d = {
             "EVENING":["evening","e","E","Evening","EVENING"],
             "MORNING":["morning","m","M","MORNING"],
             "AFTERNOON":["afternoon","a","A","AFTERNOON"],
             }
        for k,v in d.items():
            if value in v:return k
        return random.choice(list(d.keys()))

    #ok
    def clean_pay_fre(self,value):
        d = {
             "MONTHLY":["monthly","Monthly","MONTHLY"],
             "WEEKLY":["weekly","Weekly","WEEKLY"],
             "TWICEMONTHLY":["SEMI-MONTHLY","semi-monthly","Semi-Monthly","twicemonthly","TWICEMONTHLY","TwiceMonthly"],
             "BIWEEKLY":["BI-WEEKLY","Biweekly","biweekly","Bi-Weekly","BIWEEKLY","bi-weekly"]
             }
        for k,v in d.items():
            if value in v:return k
        return random.choice(list(d.keys()))
           
    #将旧表格日期整理成空格分割的"年 月 日"字符串 
    def clean_birth_date(self,value):
        #print(isinstance(value,str))
        try:
            if isinstance(value,str):
                if "/" in value:
                    day,month,year = value.split("/")
                    return "%s %s %s"%(year,month,day)
            return "%d %d %d"%(value.year,value.month,value.day)
        except:
            print("clean date error.")
            return "1976 7 13"

    def state(self,value):
        value = str(value)
        if value.upper() in datas.state.keys():return datas.state[value.upper()].upper()

        s = {v.lower():k for k,v in datas.state.items()}
        if value.lower() in s:return s[value.lower()].upper()

        print("[-] clean state filed.")
        return random.choice(list(datas.state.keys())).upper()















































