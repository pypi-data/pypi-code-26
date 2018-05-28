import math
import os

import dlib
import pickle

import cv2
import numpy as np
from sklearn.svm import SVC

clahe = cv2.createCLAHE(2.0, (8, 8))
detector = dlib.get_frontal_face_detector()
shape = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
_verbose = False

def describe(imagePath):
    towork = cv2.imread(imagePath)
    if towork is None:
        print('Unrecognized format', imagePath)
        return None

    xlist = np.empty(68, np.int)
    ylist = np.empty(68, np.int)

    # preprocessing
    towork = cv2.cvtColor(towork, cv2.COLOR_BGR2GRAY)
    towork = clahe.apply(towork)

    # face detection
    detections = detector(towork, 1)

    if len(detections) == 0:
        if _verbose:
            print("No face detected in", imagePath, 'skipped')
        return None

    rect = detections[0]
    if len(detections) > 1:
        print(detections)
        print("More that one face detected in", imagePath)
        print('\tusing:', rect)

    h, w = towork.shape
    cut = cv2.resize(towork[max(0, rect.top()):min(h, rect.bottom()), max(0, rect.left()):min(w, rect.right())], (350, 350))
    s = shape(cut, dlib.rectangle(0, 0,349 , 349))

    x0 = s.part(33).x
    y0 = s.part(33).y
    for idx in range(68):
        xlist[idx] = s.part(idx).x - x0
        ylist[idx] = s.part(idx).y - y0

    angle = -math.pi / 2 - math.atan2((ylist[27]), (xlist[27]))

    if _verbose:
        print(imagePath, 'angle', angle)

    xrot = np.int64(xlist * math.cos(angle) - ylist * math.sin(angle))
    yrot = np.int64(ylist * math.cos(angle) + xlist * math.sin(angle))

    return np.array(list(zip(xrot,yrot))).ravel()

def getEmotionDetector(dataSetPath :str = None, verbose : bool = False):
    _verbose  = verbose
    if dataSetPath is None:
        with open('SVMK18.dat','rb') as f:
            clf = pickle.load(f, fix_imports=False)
            return clf
    else:
        data = []
        labels = []
        for clase in os.scandir(dataSetPath):
            if not clase.is_dir():
                print('Ignoring no directory', clase.path)
            else:
                if verbose:
                    print('processing class:', clase.name)
                for sample in os.scandir(clase.path):
                    if verbose:
                        print('processin sample', sample.name)
                    tmp = describe(sample.path)
                    if tmp is not None:
                        data.append(tmp)
                        labels.append(clase.name)

        clf = SVC(kernel='poly', probability=True, verbose=_verbose)
        clf.fit(data, labels)
        return clf


def predictEmotion(imgPath: str, emotionDetector: SVC):
    return emotionDetector.predict([describe(imgPath)])[0]
