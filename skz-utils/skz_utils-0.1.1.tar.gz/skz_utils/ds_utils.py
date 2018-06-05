from . import os_utils
import cv2
import os
import numpy as np

def image_array_from_dir(img_dir_path, input_shape, ext, th_value=None):
    '''create image array
    '''
    img_W, img_H, img_C = input_shape
    x_list = []
    # read image
    for img_path in os_utils.get_all_files_pathList(img_dir_path, ext):
        print(img_path)
        # read image data
        if img_C == 1:
            img = cv2.imread(img_path, 0)
            if th_value is not None:
                _,img = cv2.threshold(img,th_value,255,cv2.THRESH_BINARY_INV)
        elif img_C == 3:
            img = cv2.imread(img_path, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            assert False, "<create_dataset> Invalid img_C value! {}".format(img_C)
        img = cv2.resize(img, (img_W, img_H))
        # create record
        x_list.append(img)
    # dataset
    X = np.array(x_list).reshape(-1,img_W, img_H, img_C)

    return X

def image_dataset_from_dir(img_dir_path, input_shape, ext, th_value = None):
    '''create image dataset with label from directory
    '''
    img_W, img_H, img_C = input_shape
    y_list = []
    x_list = []
    # read category
    for dir_name in os_utils.get_dir_name_list(img_dir_path):
        dir_path = os.path.join(img_dir_path, dir_name)
        # read image
        for img_path in os_utils.get_file_path_list(dir_path, ext):
            print(img_path)
            # read image data
            if img_C == 1:
                img = cv2.imread(img_path, 0)
                if th_value is not None:
                    _,img = cv2.threshold(img,th_value,255,cv2.THRESH_BINARY_INV)
            elif img_C == 3:
                img = cv2.imread(img_path, 1)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                assert False, "<create_dataset> Invalid img_C value! {}".format(img_C)
            img = cv2.resize(img, (img_W, img_H))
            # create record
            y_list.append(int(dir_name))
            x_list.append(img)
    # dataset
    y = np.array(y_list)
    X = np.array(x_list).reshape(-1,img_W, img_H, img_C)

    return y, X