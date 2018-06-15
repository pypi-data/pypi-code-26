import cv2
import base64
import json


def get_string_from_cv2(image, encode=False):
    """Gets a string from a cv2 image"""
    if encode:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        return cv2.imencode('.jpg', image, encode_param)[1].tostring()
    return cv2.imencode('.jpg', image)[1].tostring()