import numpy as np


def get_opening_degree(eye_matrix):
    # the opening degree of the eye:
    # 0.5*[y9+y8-y6-y5]/(x7-x4)
    #eye_matrix.dtype='float64'
    eye_matrix=eye_matrix.astype(float)
    #print 'matrix:',eye_matrix
    up_data=(eye_matrix[5]+eye_matrix[4]-eye_matrix[2]-eye_matrix[1])
    down_data=eye_matrix[3]-eye_matrix[0]+0.1
    #print "up_data=",up_data
    #print "down_data=",down_data
    return up_data[1]/down_data[0]
def has_closed_eye(face_landmarks):
    open_degree=np.array([0.0,0.0]);
    #print "left_eye:",face_landmarks['left_eye']
    eye_matrix=np.array(face_landmarks['left_eye'])
    #print eye_matrix[0]
    open_degree[0]=get_opening_degree(eye_matrix)
    #print "left opening degree:",open_degree[0]
    #print "right_eye:",face_landmarks['right_eye']
    eye_matrix=np.array(face_landmarks['right_eye'])
    open_degree[1]=get_opening_degree(eye_matrix)
    #print "right opening degree:",open_degree[1]
    score=open_degree.mean()
    #return open_degree.mean()>0.43,open_degree.
    return score>0.43,score
