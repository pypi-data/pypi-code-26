from pkg_resources import resource_filename

def shape_predictor_68():
    return resource_filename(__name__, "models/shape_predictor_68_face_landmarks.dat")

def shape_predictor_5():
    return resource_filename(__name__, "models/shape_predictor_5_face_landmarks.dat")

def dlib_face_recognition():
    return resource_filename(__name__, "models/dlib_face_recognition_resnet_model_v1.dat")

def human_face_detector():
    return resource_filename(__name__, "models/mmod_human_face_detector.dat")