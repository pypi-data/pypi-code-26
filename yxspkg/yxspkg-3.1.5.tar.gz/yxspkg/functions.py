#!/usr/bin/env python3
from time import strptime,mktime,strftime,localtime,time
from multiprocessing.pool import Pool,ThreadPool
from sys import stdout
__version__='1.4.0'
#modify:2017-02-03
def DaysToDate(x):
    return strftime('%Y-%m-%d',localtime((x-719163)*86400))
def DateToWeekdays(date):
    return (strptime(date, '%Y-%m-%d')[6]+1)%7
def DateToDays(x):
    return int((mktime(strptime(x,'%Y-%m-%d'))+28800)/86400+719163)
def TodayToDate(p=0):
    return DaysToDate(DateToDays(strftime('%Y-%m-%d',localtime()))+p)
#多进程测试
def ProcessesTest(target,args=[],num=None,func=Pool,callback=None):
    if num is None:p=func()
    else:p=func(num)
    if callback is 'auto':
        n=len(args)
        def CallBack(*d,count=[0,0,time(),time()]):
            count[0]+=1
            ii,ii0,start,end=count
            count[3]=time()
            t=((count[3]-start)/ii)*(n-ii)
            print('completed: {0:.3f}%, time remaining {h:.0f}:{m:02.0f}:{s:02.0f}.'.format(ii/n,h=(t//3600),m=(t%3600)//60,s=int(t%60)))
        callback=CallBack
    for i in args:
        p.apply_async(target,args=i,callback=callback)
    p.close()
    p.join()
#多线程测试
def ThreadsTest(target,args=[],num=None,callback=None):
    ProcessesTest(target=target,args=args,num=num,func=ThreadPool,callback=None)
def Record(db,Key,Value='NULL',Type='NULL'):
    # db.execute('INSERT INTO Record (`Type`,`Key`,`Value`) VALUES ({Type},{Key},{Value})  ON DUPLICATE KEY UPDATE Value={Value}'.format(Key=Key,Value=Value,Type=Type))
    db.insert('Record',Type=Type,Value=Value,Key=Key)
def Query(db,Key=None,Value=None,Type=None):
    where=list()
    if Key!=None:
        where.append('Key="'+Key+'"')
    if Value!=None:
        where.append('Value="'+Value+'"')
    if Type!=None:
        where.append('Type="'+Type+'"')
    if len(where)>0:
        where=' and '.join(where)
    else:
        where='1=1'
    x=db.select('Record',('`Type`','`Key`','`Value`'),where=where)
    return x
def Delete(db,Key=None,Value=None,Type=None):
    where=''
    if Key!=None:where+='and `Key`="%s" ' % (Key,)
    if Value!=None:where+='and `Value`="%s" ' % (Value,)
    if Type!=None:where+='and `Type`="%s" ' % (Type,)
    if len(where)==0:
        where='1=1'
    else:where=where[3:]
    db.cur.execute('delete from Record where '+where)
def Code(s,code='utf8'):
    '''输入参数可以是整数、tuple、list、字符串、其中以0x开头的字符串被认为是16进制的字符串，code是编码格式，默认utf8
    输出参数：（编码格式，整数、每个字节十进制整数，16进制的数，编码的结果）如果显示为none则认为无该编码结果'''
    htobyten=lambda h:[int(h[2+i*2:2+i*2+2],16) for i in range(int((len(h)/2)-1))]
    def htos(h):
        by=bytearray(htobyten(h))
        try:
            return by.decode(code)
        except:
            return None
    if isinstance(s,str):
        if len(s)>2 and s[:2]=='0x':
            h=s
            n=int(h,16)
            byten=htobyten(h)
            s=htos(h)
        if (len(s)>2 and s[:2]!='0x') or len(s)<=2:
            x=bytearray(s,code)
            h='0x'+''.join([hex(i)[2:].zfill(2) for i in x])
            n=int(h,16)
            byten=[int(i) for i in x]
    elif isinstance(s, tuple) or isinstance(s, list):
        x=bytearray(s)
        byten=s
        h='0x'+''.join([hex(i)[2:].zfill(2) for i in s])
        try:
            s=x.decode(code)
        except:
            s=None
        n=int(h,16)
    else:
        h=hex(s)
        n=s
        byten=htobyten(h)
        s=htos(h)
    return code,n,byten,h,s
def progress_bar(p,s1='',s2='',length=40):
	s='\r{0}|{1}|{2}'
	n1=int(p*length+0.1)
	n2=length-n1
	m1='#'*n1 
	m2=' '*n2
	stdout.write(s.format(s1,m1+m2,s2))
	stdout.flush()
if __name__=='__main__':
	pass
    # import time
    # for i in range(400):
    # 	progress_bar(i/400)
    # 	time.sleep(0.02)