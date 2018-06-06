from tkinter import *
import tkinter.filedialog as fdlg
import tkinter.messagebox
import tkinter.font 
import os
import importlib

from. import datas
from. import clean_xls


class CleanData:
  def __init__(self):
    self.root = Tk()
    self.root.title('资料整理工具 V-1.1') #
    
    self.bg = '#000000'           # 窗口背景 label 背景色
    self.text_color = "black"     # 输入框文本色
    self.bg_entry = "#a0a0a0"     # 输入框背景色
    self.ft = tkinter.font.Font(family='Fixdsys', size=18, weight=tkinter.font.BOLD)

    self.root['bg'] = self.bg
    self.string = StringVar()
    self.root.resizable(width=False,height=False)  #固定窗口大小 禁止修改
    self.xls_old_path = ""  #待整理表格文件目录
    self.xls_new_path = ""  #生成新表格的文件路径
    
  def set_lable_entry(self,row,col,text):
    Label(self.root,text=text,bg=self.bg,fg="#00ff00",font=tkinter.font.Font(size=16)).grid(row=row,column=col)#,sticky=W)
    e =Entry(self.root,bg=self.bg_entry,width=4,fg=self.text_color,font=self.ft)
    e.grid(row=row,column=col+1)
    return e


  def main(self):
    self.xls_head = list(datas.debug_data.keys())[1:]
    num = 0
    row = 0
    for i in self.xls_head:
      ele = i.replace(" ","_")
      exec("self.%s = self.set_lable_entry(num,row,i)"%ele)
      num += 1
      if not num%12:
        num = 0
        row += 2


    Label(self.root,text="资料路径:",font=tkinter.font.Font(size=16),bg=self.bg,fg="#00ff00").grid(row=15,column=4)#,sticky=W)
    self.xls_path =Entry(self.root,bg=self.bg_entry,fg=self.text_color,textvariable =self.string)
    self.xls_path.grid(row=15,column=5)
    
    Button(self.root,text = '生成新表单',bg=self.bg_entry,command = self.get_all_entry).grid(row=16,column=6) #　
    Button(self.root,text = '打  开',bg=self.bg_entry,command = self.choose_xls).grid(row=15,column=6) #　
    Button(self.root,text = 'HELP',bg=self.bg_entry,command = self.help).grid(row=16,column=5)
    self.root.mainloop()

  def get_all_entry(self):
    if not self.string.get():   #没有输入资料路径
      tkinter.messagebox.showwarning(message="请输入你要整理的表格路径!")
      return False
    
    result = {}
    
    for i in self.xls_head:
      e = i.replace(" ","_")
      data = getattr(self,e).get()
      
      if data:
        try:
          result[i] = int(data)
        except:
          tkinter.messagebox.showerror(message="输入的数据必须是整数! 请检查是否输入错误")
          return False
        
    xls_path = self.xls_path.get()
    if not os.path.isfile(xls_path):  #资料文件不存在
      tkinter.messagebox.showerror(message="文件路径输入有误,请检查输入正确路径!")
      return False

    importlib.reload(clean_xls)
    i = clean_xls.CleanXls(result,xls_path)
    
    i.main()
    #if i.dirty_data_list:tkinter.messagebox.showwarning(message=str(i.dirty_data_list))

  def help(self):
    pass
  def choose_xls(self):
    a = fdlg.askopenfilename(initialdir = self.xls_old_path)
    self.string.set(a)
    if a.endswith(".xlsx"):os.startfile(a)

if __name__ == "__main__":
  os.chdir(os.path.dirname(__file__))
  CleanData().main()





