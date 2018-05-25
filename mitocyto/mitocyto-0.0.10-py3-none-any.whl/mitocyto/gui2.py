import tkinter as tk
from PIL import ImageTk, Image, ImageDraw
import os
import mitocyto as df
import cv2
import numpy as np

def clearEdges():
    global arrs,edgeim
    arrs[-1] = np.zeros(arrs[0].shape,dtype=np.uint8)
    edgeim = Image.fromarray(arrs[-1])

def key(event):
    global img,current,ims, arrs, showedges, showcontours, draw, imtype, edgeim, contours
    curr0 = current
    k = event.keysym
    if k not in ["Shift_L","Shift_R"]:
        showcontours = False
    copying = False
    print("pressed", k)
    if k in keymap:
        i = keymap.find(k)
        if i < len(fnames):
            current = i
    if k =="x":
        print("Clearing edge image")
        clearEdges()
    if k == "c":
        copying = True
    if k == "b":
        if imtype == "threshold":
            imtype = "raw"
        else:
            imtype = "threshold"
    if k == "n":
        if imtype == "edgemap":
            imtype = "raw"
        else:
            imtype = "edgemap"
    if k == "Left":
        current = (current - 1)%len(fnames)
    if k == "Right":
        current = (current + 1)%len(fnames)
    if k == "Escape":
        root.destroy()
        root.quit()
    if k == "space":
        showcontours = not showcontours
    if k == "z":
        showedges = not showedges
    #if showcontours and current is not curr0:
    #    showcontours = False
    if showedges and current is not curr0:
        showedges = False
    if showedges and current is curr0:
        current = -1
    if not modifier:
        if showcontours:
            arrs[-1] = np.array(edgeim, dtype=np.uint8)
            imnew,contours = df.makeContours(df.makepseudo(arrs[-1]),showedges)
            title = "Contours"
            #C.delete("dot")
            root.title(title)
            img = ImageTk.PhotoImage(imnew.resize((wnew,hnew),Image.ANTIALIAS))
            C.itemconfig(C_image, image=img)
            #showcontours = False
        else:
            title = fnames[current]+" "+keymap[current]
            if imtype == "raw":
                arrnew = arrs[current]
                title = "Raw "+title
            if imtype == "threshold":
                arrnew = df.getthresh(arrs[current])
                title = "Threshold "+title  
            if imtype == "edgemap":
                arrnew = df.edgesFromGrad(arrs[current],block_size=51)
                title = "Edgemap "+title
            if current == -1 or current == len(arrs) - 1:
                imnew = edgeim
            else:
                imnew = Image.fromarray(df.makepseudo(arrnew))
            #if current is not curr0:
            C.delete("dot")
            root.title(title)
            img = ImageTk.PhotoImage(imnew.resize((wnew,hnew),Image.ANTIALIAS))
            C.itemconfig(C_image, image=img)
    if copying:
        print("Copying current image to edge image")
        arrs[-1] = np.array(edgeim, dtype=np.uint8)
        arrs[-1] = np.maximum(arrs[-1],arrnew)
        edgeim = Image.fromarray(df.makepseudo(arrs[-1]))
        draw = ImageDraw.Draw(edgeim)

def paint(event, colour = "white", rad = 2, sclx=1.0, scly=1.0):
    global draw, edgeim
    if not modifier:
        x1, y1 = ( event.x - rad ), ( event.y - rad )
        x2, y2 = ( event.x + rad ), ( event.y + rad )
        C.create_oval( x1, y1, x2, y2, fill = colour, outline=colour, tags="dot")
        if colour == "white": pcolour = 255
        if colour == "black": pcolour = 0
        draw.ellipse((int(round(float(x1)/sclx)), int(round(float(y1)/scly)), int(round(float(x2)/sclx)), int(round(float(y2)/scly))), fill = pcolour, outline=pcolour)

def fillcontour(event):
    global arrs, contours, edgeim, draw
    point = (int(round(float(event.x)/sclx)), int(round(float(event.y)/scly)))
    clicked = [(i,cnt) for i,cnt in enumerate(contours) if cv2.pointPolygonTest(cnt, point, measureDist = False) >= 0]
    for i,cnt in clicked:
        print("Deleting contour number "+str(i+1))
        cv2.drawContours(arrs[-1],[cnt],-1,(255),cv2.FILLED)
    edgeim = Image.fromarray(df.makepseudo(arrs[-1]))
    draw = ImageDraw.Draw(edgeim)

def checkmod(event, modkeys = ["Shift_L","Shift_R"], press = True):
    global modifier
    if event.keysym in modkeys:
        if modifier is not press:
            modifier = press
            print("Modifier: "+str(modifier))
    elif press:
        key(event)

if __name__=="__main__":
    keymap = "1234567890qwertyuiopasdfghjkl"
    add_edit = "mitoim.png"
    folder = "."
    output = "."

    showedges = False
    showcontours = False
    modifier = False
    imtype = "raw"

    allfiles = os.listdir(folder)
    allfiles = [f for f in allfiles if os.path.splitext(f)[1] in [".tiff",".TIFF",".jpg",".JPG",".jpeg",".JPEG",".png",".PNG"]]
    files = [f for f in allfiles if add_edit not in f]
    files.sort()

    edge = "Dystrophin"
    isedge = [edge.lower() in f.lower() for f in files]
    edgeind = [i for i, x in enumerate(isedge) if x]
    if len(edgeind)>0:
        current = edgeind[0]
    else:
        current = 0

    arrs = [np.array(Image.open(f)) for f in files]
    #ims = [Image.fromarray(df.makepseudo(arr)) for arr in arrs]
    #ims = [Image.fromarray(df.makepseudo(np.array(Image.open(f)))) for f in files]
    bigarr = np.zeros(arrs[0].shape+(sum([not i for i in isedge]),),dtype=np.uint8)
    ind = 0
    for i,arr in enumerate(arrs):
        if not isedge[i]:
            bigarr[:,:,ind]=arr
            ind += 1
    maxarr = np.max(bigarr,2)
    meanarr = np.mean(bigarr,2)
    medianarr = np.median(bigarr,2)
    bigarr = None

    arrs = arrs + [meanarr,None]
    clearEdges()
    fnames = files + ["Mean","Edges"]

    edgemapfile = os.path.join(output,"EDGE_"+add_edit)
    if os.path.isfile(edgemapfile):
        edgeim = Image.open(edgemapfile)
        arrs[-1] = np.array(edgeim,dtype=np.uint8)

    edgeim = Image.fromarray(df.makepseudo(arrs[-1]))
    draw = ImageDraw.Draw(edgeim)
    h,w = arrs[current].shape

    #Start the GUI
    root = tk.Tk()
    root.title(fnames[current]+" "+keymap[current])

    # Prepare to resize images to fit in screen, if necessary
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    if w>screen_width:
        scl = float(screen_width)/float(w)
    if scl*h>screen_height:
        scl = float(screen_height)/float(h)

    wnew,hnew = int(round(scl*w)), int(round(scl*h))
    sclx,scly = float(wnew)/float(w), float(hnew)/float(h)

    img = ImageTk.PhotoImage(Image.fromarray(df.makepseudo(arrs[current])).resize((wnew,hnew),Image.ANTIALIAS))
    C = tk.Canvas(root,width = wnew, height = hnew)
    C_image = C.create_image(0,0,image=img,anchor='nw')

    C.focus_set()
    C.bind("<B1-Motion>", lambda event: paint(event, colour = "white", rad = 2*scl, sclx = sclx, scly = scly))
    C.bind("<B3-Motion>", lambda event: paint(event, colour = "black", rad = 5*scl, sclx = sclx, scly = scly))
    C.bind("<Shift-Button-1>", lambda event: fillcontour(event))
    C.bind("<KeyPress>", lambda event:  checkmod(event,press = True))
    C.bind("<KeyRelease>", lambda event: checkmod(event,press = False))
            
    C.pack()

    root.mainloop()

    timer = df.startTimer()
    print("Saving edited cell membrane file... "+str(timer()))
    Image.fromarray(df.makepseudo(arrs[-1])).save(edgemapfile)
    print("Getting contours & saving preview... "+str(timer()))
    arr = arrs[-1]
    arrs = None

    rgb,contours = df.makeContours(df.makepseudo(arr))
    rgb.save(os.path.join(output,"CONTOURS_"+add_edit))
    print("Building masks from contours... "+str(timer()))
    masks = [df.makemask(arr.shape,cnt) for cnt in contours]
    print("Building measures from contours... "+str(timer()))
    centres = [df.getcentre(cnt) for cnt in contours]
    areas = [cv2.contourArea(cnt) for cnt in contours]
    aspects = [df.getaspect(cnt) for cnt in contours]
    perims = [cv2.arcLength(cnt,True) for cnt in contours]
    circs = [df.circularity(cnt) for cnt in contours]

    print("Opening channel images... "+str(timer()))
    fnames = fnames[0:-2]
    froots = [fname.strip(".ome.tiff") for fname in fnames]
    images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
    arrays = {froot:np.array(images[froot],dtype=np.int) for froot in froots}
    #psims = {froot:df.arrtorgb(arrays[froot]) for froot in froots}

    print("Average values for each contour mask in each image... "+str(timer()))
    avelogs = {froot:[np.mean(np.log(arrays[froot][msk[0],msk[1]]+1)) for msk in masks] for froot in froots}
    fracpos = {froot:[np.sum(arrays[froot][msk[0],msk[1]]>0)/len(msk[0]) for msk in masks] for froot in froots}

    print("Writing output to text file... "+str(timer()))
    res = open(os.path.join(output,"results.csv"),"w")
    res.write("Value,ID,Channel,Folder 1,Filename\n")

    for j,froot in enumerate(froots):
        print("Writing "+froot+" results to file... "+str(timer()))
        res.writelines("\n".join([",".join([str(ml),str(i+1),froot,os.path.abspath(folder).split("\\")[-1],os.path.abspath(os.path.join(folder,fnames[j]))]) for i,ml in enumerate(avelogs[froot])]))
        res.write("\n")
    res.close()
