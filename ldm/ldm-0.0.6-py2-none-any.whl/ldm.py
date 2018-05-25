import os
import dlib
from skimage import io
import numpy as np

class LDM:
    def __init__(self):
        self.predictor_path="landmarks_68.dat"
        url='http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
        self.predictor_path=self.get_model(url,self.predictor_path) 
        self.detector=dlib.get_frontal_face_detector()
        self.predictor=dlib.shape_predictor(self.predictor_path)
        
        self.face_rec_model_path='face_rec.dat'
        url="http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
        self.face_rec_model_path=self.get_model(url,self.face_rec_model_path)
        print self.face_rec_model_path 
        self.facerec = dlib.face_recognition_model_v1(self.face_rec_model_path)


    def get_part_landmarks(self,shape,start_index,end_index):
        '''
        {   
            dxRange jaw;       // [0 , 16]
            IdxRange rightBrow; // [17, 21]
            IdxRange leftBrow;  // [22, 26]
            IdxRange nose;      // [27, 35]
            IdxRange rightEye;  // [36, 41]
        IdxRange leftEye;   // [42, 47]
        IdxRange mouth;     // [48, 59]
        IdxRange mouth2;    // [60, 67]
        }
        make the shape to be a dict that can easy get  part like jaw,brow,nose,eye,mouth
        '''
        jaw=[]
        for i in range(start_index,end_index):
            #print i+1,shape.part(i)
            jaw.append(np.array((shape.part(i).x,shape.part(i).y)))
        return jaw
    
    def landmark_list(self,img):
        # get all 68 landmarks from the img
        # return the list ldl of the landmark dict ld
        dets = self.detector(img, 1)
        #print("Number of faces detected: {}".format(len(dets)))
        ldl=[]
        facel=[]
        for k,d in enumerate(dets):
            shape=self.predictor(img,d)
            #print k,d
            ld={'help':'jaw,right_brow,left_brow,nose,right_eye,left_eye,mouth,mouth2'}
            ld['jaw']=self.get_part_landmarks(shape,0,17)
            ld['right_brow']=self.get_part_landmarks(shape,17,22)
            ld['left_brow']=self.get_part_landmarks(shape,22,27)
            ld['nose']=self.get_part_landmarks(shape,27,36)
            ld['right_eye']=self.get_part_landmarks(shape,36,42)
            ld['left_eye']=self.get_part_landmarks(shape,42,48)
            ld['mouth']=self.get_part_landmarks(shape,48,59)
            ld['mouth2']=self.get_part_landmarks(shape,60,67)
            ldl.append(ld)
            facel.append(d)
        #for ld in ldl:
        #    print ld['right_eye']
            #print np.array(ld)
        return ldl,facel
    
    def get_model(self,url,predictor_path):
        #predictor_path="landmarks_68.dat"
        #url='http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
        if not os.path.exists(predictor_path):
            print os.path.exists("%s.bz2"%(predictor_path))
            if not os.path.exists("%s.bz2"%(predictor_path)):
                os.system('wget -O %s.bz2 %s'%(predictor_path,url))   
            os.system('bunzip2 %s.bz2'%(predictor_path))   
        return predictor_path
    
    def landmarks(self,img):
       
        #predictor_path=get_model() 
        #detector=dlib.get_frontal_face_detector()
        #predictor=dlib.shape_predictor(predictor_path)
        ldl,facel=self.landmark_list(img)
        helptxt='dict[0]_item:jaw,right_brow,left_brow,nose,right_eye,left_eye,mouth,mouth2'
        return ldl,facel,helptxt+',model_paht='+self.predictor_path
    
    def face_area_rate(self,img,facel):
        #the rectangle area of face vs the area of img
        ratel=[]
        for face in facel:
            rate=float(face.width())*float(face.height())
            rate/=float(img.shape(0)) 
            rate/=float(img.shape(1))
            ratel.append(rate) 
        return ratel
    def face_number(self,img,facel):
        face_num=len(facel)
        return face_num

    def face_center_degree(self,img,ldl,facel):
        xdl=[]
        ydl=[]
        mdl=[]
        for face in facel:
            
            xd=float(face.left())+float(face.right())
            xd/=2
            xd=abs(xd-float(img.shape[0])/2)
            xd/=float(img.shape[0])/2
            xd=1-xd

            yd=float(face.top())+float(face.bottom())
            yd/=2
            yd=abs(xd-float(img.shape[1])/2)
            yd/=float(img.shape[1])/2
            yd=1-yd

            md=(xd+yd)*0.5
            xdl.append(xd)
            ydl.append(yd)
            mdl.append(md)
        return xdl,ydl,mdl
    def face_feature(self,img,facel):
        #ldl,facel,helptxt=self.landmarks(img)
        ffl=[]
        face_index=0
        for face in facel:
            shape = self.predictor(img, face)
            face_descriptor = self.facerec.compute_face_descriptor(img, shape)
            ffl.append(face_descriptor)
            face_index+=1
        return ffl
    def normalized_sigmoid_fkt(self,a, b, x):
       '''
       Returns array of a horizontal mirrored normalized sigmoid function
       output between 0 and 1
       Function parameters a = center; b = width
       '''
       s= 2/(1+np.exp(b*(x-a)))
       #return 1*(s-min(s))/(max(s)-min(s)) # normalize function to 0-1    
       return s    
    
    def face_compare(self,feature1,feature2,dist_type='cosine'):
        vec1=np.array(feature1)
        #print vec1
        vec2=np.array(feature2)
        if dist_type=='euclidean':
           dist_euclidean=np.linalg.norm(vec1 - vec2)
           dist=dist_euclidean       
        if dist_type=='manhattan':
           dist_manhattan=np.linalg.norm(vec1 - vec2,ord=1)       
           dist=dist_manhattan       
        if dist_type=='chebyshev':
           dist_chebyshev=np.linalg.norm(vec1 - vec2,ord=np.inf)
           dist=dist_chebyshev       
        if dist_type=='cosine':
           dist_cosine=np.dot(vec1,vec2)/(np.linalg.norm(vec1)*(np.linalg.norm(vec2)))
           dist=dist_cosine       
         
        return self.normalized_sigmoid_fkt(0,1,dist),dist
    def compare_ffl(self,ff1l,ff2l):
        scorel=[]
        index1l=[]
        index2l=[]
        ic1=0
        ic2=0
        for ff1 in ff1l:
            for ff2 in ff2l:
                score,sscore=self.face_compare(ff1,ff2,'euclidean')
                scorel.append(score)
                index1l.append(ic1)
                index2l.append(ic2)
                ic2+=1
            ic1+=1
        return scorel,index1l,index2l
        
    def face_rec(self,img1,img2,threshold=0.8):
        ld1l,face1l,t=self.landmarks(img1)
        ld2l,face2l,t=self.landmarks(img2)
        ff1l=self.face_feature(img1,face1l);
        ff2l=self.face_feature(img2,face2l);
        scorel,index1l,index2l=self.compare_ffl(ff1l,ff2l)
        for i in range(0,len(scorel)):
            index=len(scorel)-i-1
            if scorel[index]<threshold:
                del scorel[index]
                del face1l[index]
                del face2l[index]
                del index1l[index]
                del index2l[index]

        result_dict={'scorel':scorel,
               'face1l':face1l,
               'face2l':face2l,
               'index1l':index1l,
               'incex2l':index2l}
        return result_dict
 
    def has_same_person(self,img1,img2,threshold=0.8):
        ldl1,face1l,t=self.landmarks(img1)
        ldl2,face2l,t=self.landmarks(img2)
        ff1l=self.face_feature(img1,face1l);
        ff2l=self.face_feature(img2,face2l);
        scorel,index1l,index2l=self.compare_ffl(ff1l,ff2l)
        sarray=np.array(scorel)
        sarray=sarray>threshold
        return np.sum(sarray)


 
