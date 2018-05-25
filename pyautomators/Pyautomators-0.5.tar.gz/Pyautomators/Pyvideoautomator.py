import numpy as np
import cv2
from PIL import ImageGrab

def gravar_video(xi, yi, xf, yf,path_name):
    


    fourcc = cv2.VideoWriter_fourcc('X','V','I',"D") #you can use other codecs as well.
    vid = cv2.VideoWriter(path_name,fourcc, 2, (xf,yf))
    while True :
        img = ImageGrab.grab(bbox=(xi, yi, xf, yf)) #x, y, w, h
        img_np = np.array(img)
        #frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        vid.write(img_np)
        key = cv2.waitKey(1)
        if key == 27:
            break    
    
    vid.release()
    cv2.destroyAllWindows()