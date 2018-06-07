#!/usr/bin/env python3
import time,requests,re
import tushare
session=requests.Session()
session.headers={'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate',
'DNT': '1',
'Connection': 'keep-alive'}
def GetDataFromSina(stockID,date1=None,date2=None,stockExchange=None):
    if date1 is None:date1=(1700,1,1)
    else:date1=tuple(date1)
    if date2 is None:date2=(2700,12,10)
    else:date2=tuple(date2)
    url='http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/%s.phtml' % (stockID,)
    session.headers['Host']='money.finance.sina.com.cn'
    dataPattern=re.compile(r'(\d\d\d\d-\d\d?-\d\d?)""(\d*\.?\d+)""(\d*\.?\d+)""(\d*\.?\d+)""""(\d*\.?\d+)""""(\d*)""""(\d*)')
    columns=dict(zip(('Date','Open','High','Close','Low','Volume','Value'),range(7)))
    def GetYear():
        p=re.compile(r'<option value="(\d\d\d\d)" ')
        x=session.get(url)
        return p.findall(x.text)
    def GetData(params0):
        x=session.get(url,params=params0)
        d=re.sub(r'[^\.0-9"-]','',x.text)
        return dataPattern.findall(d)
    years=[int(i) for i in GetYear() if int(i)>=date1[0] and int(i)<=date2[0]]
    years.sort()
    if len(years)==0:return None,[]
    if len(years)==1:years*=2
    jidu1,jidu2=int((date1[1]-1)//3)+1,int((date2[1]-1)//3)+1
    year=years[0]
    yearEnd=years[-1]
    a=[]
    while year*10+jidu1<=yearEnd*10+jidu2:
        params={'year':str(year),'jidu':str(jidu1)}
        x=GetData(params)
        a.extend(x)
        jidu1+=1
        if jidu1==5:
            jidu1=1
            year+=1
    if date1 is not None and len(a)>0:
        date1='%4d-%02d-%02d' % date1
        a=[i for i in a if i[0]>=date1]
    if date2 is not None and len(a)>0:
        date2='%4d-%02d-%02d' % date2
        a=[i for i in a if i[0]<=date2]
    return columns,a
def GetDataFromTencent(stockID,date1=None,date2=None,stockExchange='None'):
    url='http://data.gtimg.cn/flashdata/hushen/latest/daily/%s.js?maxage=43201'
    session.headers['Host']='data.gtimg.cn'
    if stockExchange.lower() not in ('ss','sz'):return None,None
    url=url % (stockExchange.lower()+stockID,)
    d=session.get(url)
    d=d.text.replace('\\n\\','00').split('\n')[2:-1]
    d=[i.split() for i in d]
    if date1 is not None and len(d)>0:
        date1=('%4d%02d%02d' % date1)[2:]
        d=[i for i in d if i[0]>=date1]
    if date2 is not None and len(d)>0:
        date2=('%4d%02d%02d' % date2)[2:]
        d=[i for i in d if i[0]<=date2]
    f=lambda x:'19' if x[0]>'7' else '20'
    d=[('%s%s-%s-%s' % (f(i),i[:2],i[2:4],i[4:]), j,k,l,m,n) for i,j,k,l,m,n in d]
    return {'Date':0,'Open':1,'Close':2, 'High':3,'Low':4,'Volume':5},d
def GetDataFromYahoo(stockID,date1=None,date2=None,stockExchange='None'):
    url0='http://table.finance.yahoo.com/table.csv?s=%s'
    session.headers['Host']='table.finance.yahoo.com'
    if stockExchange.lower() in ['sz','ss']:stockID=stockID+'.'+stockExchange
    params=[stockID]
    if date1 is not None:
        url0+='&c=%s&a=%s&b=%s'
        params.extend(date1)
        params[-2]-=1
    if date2 is not None:
        url0+='&f=%s&d=%s&e=%s'
        params.extend(date2)
        params[-2]-=1
    url=url0 % tuple(params)
    r=session.get(url).text.split('\n')
    if r[0].find('Date')==-1:return None,[]
    columns=dict(zip(('Date','Open','High','Low','Close','Volume','AdjClose'),range(7)))
    return columns,[i.split(',') for i in r[1:-1]]
def GetDataFromHexun(stockID,date1=(2016,5,2),date2=(2016,10,9)):
    url='http://webstock.quote.hermes.hexun.com/a/kline?code=sse601398&start=20150909150000&number=-10&type=5' % (stockID,)
    session.headers['Host']='money.finance.sina.com.cn'
    dataPattern=re.compile(r'(\d\d\d\d-\d\d?-\d\d?)""(\d*\.?\d+)""(\d*\.?\d+)""(\d*\.?\d+)""""(\d*\.?\d+)""""(\d*)""""(\d*)')
    columns='Date','Open','High','Close','Low','Volume','Value'
    def GetYear():
        p=re.compile(r'<option value="(\d\d\d\d)" ')
        x=session.get(url)
        return p.findall(x.text)
    def GetData(params0):
        x=session.get(url,params=params0)
        d=re.sub(r'[^\.0-9"-]','',x.text)
        return dataPattern.findall(d)
    years=[int(i) for i in GetYear() if int(i)>=date1[0] and int(i)<=date2[0]]
    if len(years)==1:years*=2
    jidu1,jidu2=int((date1[1]-1)//3)+1,int((date2[1]-1)//3)+1
    year=years[0]
    yearEnd=years[-1]
    a=[]
    while year*10+jidu1<=yearEnd*10+jidu2:
        print(year,jidu1)
        params={'year':str(year),'jidu':str(jidu1)}
        x=GetData(params)
        a.extend(x)
        jidu1+=1
        if jidu1==5:
            jidu1=1
            year+=1
    return columns,a
def GetDataFromTushare(stockID,date1=None,date2=None,stockExchange='None'):
    x=tushare.get_k_data(stockID,'%04d-%02d-%02d' % date1,'%04d-%02d-%02d' % date2)
    t=zip(x['date'],x['open'],x['close'],x['high'],x['low'],x['volume'])
    return {'Date':0,'Open':1,'Close':2, 'High':3,'Low':4,'Volume':5},list(t)
def GetHistoryData(stockID,date1=None,date2=None,stockExchange='None',source='Sina'):
    if source.lower()=='yahoo':API=GetDataFromYahoo
    elif source.lower()=='tencent':API=GetDataFromTencent
    elif source.lower()=='sina':API=GetDataFromSina
    else:API=GetDataFromTushare
    return API(stockID=stockID,date1=date1,date2=date2,stockExchange=stockExchange)
def GetRealTimeData(stockID,stockExchange='None'):
    label={'ss':'sh','sz':'sz','sh':'sh'}
    key=label.get(stockExchange.lower())
    if key == None:return False
    url='http://hq.sinajs.cn/list=%s%s' % (key,stockID)
    s=requests.get(url).text
    s=s[s.find('"')+1:].split(',')
    d={'ID':stockID,'Date':s[-3],'Open':float(s[1]),'Current':float(s[3]),'High':float(s[4]),'Low':float(s[5]),'Close':float(s[3]),'Volume':-1,'ChineseName':s[0],'Time':s[-2]}
    return d
if __name__=='__main__':
    d,t=GetDataFromTushare('002524',date1=(2017,2,24),date2=(2017,2,27))
    d,t2=GetDataFromSina('002524',date1=(2017,2,24),date2=(2017,2,27))
    t2.sort(key=lambda x:x[0])
    for i,j in zip(t,t2):
        print(i,'\n',j)