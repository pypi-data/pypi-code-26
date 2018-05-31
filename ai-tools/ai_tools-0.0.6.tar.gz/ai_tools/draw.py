#!/usr/bin/python
import cv2
from save2server import *
import numpy as np
import random
def norm(x,norm_range):
    '''
      normlize the value of x between the norm_range
      x: a numpy array
      norm_range : a numpy array, the first element is the low value,and the second is the high value
    '''
    x_=np.array(x)
    x_=(x_-x_.min())*(norm_range.max()-norm_range.min())/(x_.max()-x_.min())
    #print " input:{}".format(x)
    #print " range:{}".format(norm_range)
    #print "output:{}".format(x_)
    return x_
def putText(img,title,pos,font,scale,c,thinck_ness,direction='h'):
    '''
    write text on the image,use the opencv lib
      direction :  'h' mean write the text horizontally
                   'v' mean write the text vartically
                   'v1' mean write the text horizontally and rotate the image 90 degree
            img : 
          title : 
            pos :  position like (100,100)
           font :  open cv font,like 
          scale :  opencv scale
              c :  color like (255,0,255)
     think_ness : 
    '''
    #print c
    if direction=='h':
       npos=np.array(pos)
       width=npos[0]
       height=npos[1]
       npos=([int((width-len(title)*18*scale)/2), int(height/7*4)])
       pos=tuple(npos)
       cv2.putText(img,title,pos,font,scale,c,thinck_ness)
    elif direction=='v':
       npos=np.array(pos)
       width=npos[0]
       height=npos[1]
       npos=([int(width/7*4), int(height/len(title))])
       pos=tuple(npos)
       for x in title:
           npos=np.array(pos)
           npos[1]+=24*scale
           pos=tuple(npos)
           cv2.putText(img,x,pos,font,scale,c,thinck_ness)
    elif direction=='v1':
       #print 'img shape:{},dtype:{}'.format(img.shape,img.dtype)
       img_tmp=np.rot90(img,1,(1,0))
       #print 'img_tmp shape:{},dtype:{}'.format(img_tmp.shape,img_tmp.dtype)
       npos=np.array(pos)
       width=npos[1]
       height=npos[0]
       img_tmp=np.zeros((height,width,3),np.uint8)+255
       #npos=([int(width/len(title)), int(height/7*4)])
       npos=([int((width-len(title)*18*scale)/2), int(height/7*4)])
       pos=tuple(npos)
       #print pos
       cv2.putText(img_tmp,title,pos,font,scale,c,thinck_ness)
       #save2server('temp.jpg',img_tmp)
       img=np.rot90(img_tmp,1,(0,1))
       save2server('temp.jpg',img_tmp)
       img=np.rot90(img_tmp,1,(0,1))
       #print 'img shape:{},dtype:{}'.format(img.shape,img.dtype)
    return img 
def draw_text(title,width,height,text_scale='50',c=(10,10,10),direc='h'):
    img=np.zeros((height,width,3),np.uint8)+255
    font = cv2.FONT_HERSHEY_SIMPLEX
    #font=cv2.InitFont(cv2.FONT_HERSHEY_SIMPLEX)
    #c=(10,10,10)
    #print 'font.vscale={}'.format(font.vscale)
    #cv2.putText(img, title, (int(width/len(title)), int(height/7*4)), font, np.min([height,width])/70, c, 2)
    img=putText(img, title, (width,height), font, text_scale, c, 2,direc)
    return img     
def draw_curve(x,y,width=512,height=512,title='title',xlabel='xlabel',ylabel='ylabel'):
    x=norm(x,np.array([0,width]))
    y=norm(y,np.array([0,height]))
    x=x.astype('int32')
    y=y.astype('int32')
    #print x.dtype
    #print y.dtype
    img = np.zeros((height,width,3),np.uint8)#create a color none content img
    img=img+255
    num=7*2
    width_pre=int(width/num) 
    height_pre=int(height/num) 
    for i in range(0,num+1):
       for j in range(0,num+1):
           stx=i*width_pre
           sty=j*height_pre
           cv2.rectangle(img,(stx,sty),(width_pre,height_pre),(128,128,128),1)
    cv2.rectangle(img,(0,0), (width,height), (0,0,0),3)
    line_color=(0,0,255)
    for i in range(0,len(x)):
        if i==0:
            cv2.line(img,(0,height-0),(x[i+1],height-y[i+1]),line_color,3)
        elif i==len(x)-1:
            print("draw line done")
        else:
            cv2.line(img,(x[i],height-y[i]),(x[i+1],height-y[i+1]),line_color,3)
    title_height=int(height*0.2)
    xlabel_width=int(width*0.2)
    text_scale=np.min([width,height])/350
    imgxlabel=draw_text(xlabel,width,title_height,text_scale)
    imgylabel=draw_text(ylabel,xlabel_width,height+title_height,text_scale,direc='v1')
    imgtitle=draw_text(title,width+xlabel_width,title_height,text_scale)
    imgvipkid=draw_text("vipkid bgdata group",xlabel_width,height+title_height*2,text_scale,(168,168,168),'v1')
    #print imgtitle.shape
    #print img.shape
    img=np.vstack((img,imgxlabel))    
    img=np.hstack((imgylabel,img))    
    img=np.vstack((imgtitle,img))
    img=np.hstack((img,imgvipkid))    
    save2server("roc{}.jpg".format(random.random()),img)
    return img
def image2text(img,dst_size=(80,80)):
    # img2gray
    img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
         
    # img2bw
    img_bw= image2bw(img_gray)
   
    # imgresize
    print img_bw.shape
    rows, cols = img_bw.shape
    img_rs = cv2.resize(img_bw, dst_size, interpolation=cv2.INTER_CUBIC)
    rows, cols = img_rs.shape

    # pixel 2 charactors
    text_pic=''
    im=img_rs
    save2server('tmp.jpg',im)
    for i in range(0,rows):
        for j in range(0,cols):
                 
                   if im[i,j] >128: # operate every pixel
                       text_pic+=' '
                   else:
                       text_pic+='#'
        text_pic+='\r\n'
    print str(text_pic)
    print im
    return text_pic



def add_random_value():
    for k in range(5000): #Create 5000 noisy pixels
        i = random.randint(0,im.height-1)
        j = random.randint(0,im.width-1)
        color = (random.randrange(256),random.randrange(256),random.randrange(256))
    img[i,j] = color    
    return img
def image2bw(GrayImage,method='adaptive_gaussian'):
    # mean filter 
    GrayImage= cv2.medianBlur(GrayImage,5)
    if method=='adaptive_gaussian': 
        th = cv2.adaptiveThreshold(GrayImage,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,3,5) 
    elif method=='adaptive_mean':#3->Block size, 5->param1  
        th = cv2.adaptiveThreshold(GrayImage,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,5)
    else: 
        ret,th = cv2.threshold(GrayImage,127,255,cv2.THRESH_BINARY) 
    return th
def example_zmm():
    # read the original
    img = cv2.imread('../test2.jpg')
    #cv2.imshow('original', img)
    
    # expand
    rows, cols, channels = img.shape
    img_ex = cv2.resize(img, (2*cols, 2*rows), interpolation=cv2.INTER_CUBIC)
    #cv2.imshow('expand', img_ex)
    
    # zoom
    img_zo = cv2.resize(img, (cols/2, rows/2), interpolation=cv2.INTER_AREA)
    #cv2.imshow('zoom', img_zo)
    
    # trans
    M = np.array([[1, 0, 50],[0, 1, 50]], np.float32)
    cv2.imshow('trans', img_tr)
    #cv2.imshow('trans', img_tr)
    
    # Rotation
    M=cv2.getRotationMatrix2D((cols/2,rows/2), 45, 1)
    img_ro =cv2.warpAffine(img, M, img.shape[:2]) 
def getBluePixel(Img):
    HSV = cv2.cvtColor(Img, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(HSV)
    LowerBlue = np.array([100, 100, 50])
    UpperBlue = np.array([130, 255, 255])
    mask = cv2.inRange(HSV, LowerBlue, UpperBlue)
    BlueThings = cv2.bitwise_and(Img, Img, mask=mask)
def test():
    x=np.array([-0.2,0.3,0.4,0.5])
    y=np.array([0.2,0.4,0.1,-0.4])
    norm(x,np.array([0,500]))
    
    img=draw_curve(x,y)
    #img=cv2.imread('../examples/faces/2007_007763.jpg')
    #print img.shape 
    #image2text(img,(80,40))
if __name__=='__main__':
    x=np.array([-0.2,0.3,0.4,0.5])
    y=np.array([0.2,0.4,0.1,-0.4])
    norm(x,np.array([0,500]))
    



    img=draw_curve(x,y)
    #img=cv2.imread('../examples/faces/2007_007763.jpg')
    print img.shape 
    image2text(img,(80,40))
    image2text(img,(80,40))
