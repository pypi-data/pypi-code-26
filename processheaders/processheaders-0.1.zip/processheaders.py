#coding:utf-8

from fake_useragent import UserAgent
from urllib.parse import urlparse

class Headers(object):
    '''自动解析链接并构造浏览器headers'''
    ua=UserAgent()
    def __init__(self,link,cookies=None,*args):
        headers={}
        headers['Accept']="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        headers['Accept-Encoding']='gzip, deflate, br'
        headers['Accept-Language']='zh-CN,zh;q=0.9'
        headers['Cache-Control']='max-age=0'
        headers['Connection']='keep-alive'
        headers['DNT']='1'
        headers['Upgrade-Insecure-Requests']='1'
        url=urlparse(link)
        headers["Host"]=url.hostname
        headers['Referer']=url.scheme+'://'+url.netloc
        headers['User-Agent']=self.ua.random     
        return headers

    def Headers(path):
        '''格式化headers为字典，输入path的文件路径'''
        ftp=open(path,'r+')
        data=ftp.readlines()
        ftp.close()
        headers={}
        for i in data:
            i=i.strip()
            n=i.count(':')
            if n==1:
                a,b=i.split(':')             
            elif n>1:
                ch=i.split(':')
                a=ch[0]
                b=i[len(a)+1:]
            headers[a.strip()]=b.strip()  
        return headers
