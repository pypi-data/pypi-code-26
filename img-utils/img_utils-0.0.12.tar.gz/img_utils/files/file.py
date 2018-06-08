import glob
import os


def images_in_dir(images_dir, file_types=('*.png', '*.jpg', '*.jpeg', '*.gif')):
    """
    :param images_dir: directory that contains target images
    :param file_types: image files extend
    :return: full image file path list
    """
    file_names = []
    for ext in file_types:
        file_names.extend(glob.glob(os.path.join(images_dir, ext)))
    return sorted(file_names)


def filename(file_path):
    """
    :param file_path: file path
    :return: file name with extend
    """
    return file_path.split(os.sep)[-1]


def fname(file_name):
    """
    :param file_name: file name or file path
    :return: file name without extend
    """
    idx = file_name.rindex(os.extsep)
    return file_name[0:idx]
