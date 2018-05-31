#!/usr/bin/python
import cv2

def save2server(imgname,img):
    ret=cv2.imwrite('/data1/mingmingzhao/data_sets/test/race_recog/'+imgname,img)
    print "local url is /data1/mingmingzhao/data_sets/test/race_recog/{}".format(imgname)
    print "remote url is http://192.168.7.37:8393/static/race_recog/{}".format(imgname)
    print "<img src='http://192.168.7.37:8393/static/race_recog/{}' title={} />".format(imgname,imgname)
    print "or u can view the image at :http://192.168.7.37:8393/show/?start_num=1&length=200&dirname=/{}".format(imgname.split('/')[:-1])
    return ret
