import os
import shutil
import gzip

# Third party
import requests
import numpy as np

# Internal
from deep_teaching_commons import config


class Mnist:
    """Downloads, loads into numpy array and reshapes the common machine learning dataset: MNIST

    The MNIST dataset contains handwritten digits, available from http://yann.lecun.com/exdb/mnist/,
    has a training set of 60,000 examples, and a test set of 10,000 examples. With the class you can
    download the dataset and prepare them for usage, e.g., flatten the images or hot-encode the labels.
    """

    def __init__(self, data_dir=None, auto_download=True, verbose=True):
        """Downloads and moves MNIST dataset in a given folder.

        MNIST will be downloaded from http://yann.lecun.com/exdb/mnist/ and moved
        into the folder 'data_dir', if a path is given by the user, else files
        will be moved into a folder specified by the deep-teaching-commons
        config file.

        Args:
            data_dir: A string representing a path where you want to store MNIST.
            auto_download: A boolean, if True and the given 'data_dir' does not exists, MNIST will be download.
            verbose: A boolean indicating more user feedback or not.
        """
        self.data_dir = data_dir
        self.verbose = verbose

        if self.data_dir is None:
            self.data_dir = os.path.join(config.BASE_DATA_DIR, 'MNIST')

        self.data_url = 'http://yann.lecun.com/exdb/mnist/'
        self.files = ['train-images-idx3-ubyte.gz','train-labels-idx1-ubyte.gz','t10k-images-idx3-ubyte.gz', 't10k-labels-idx1-ubyte.gz']

        if auto_download:
            if self.verbose:
                print('auto download is active, attempting download')
            self.download()

    def download(self):
        """Downloads MNIST dataset.

        Creates a directory, downloads MNIST and moves the data into the
        directory. MNIST source and target directory are defined by
        class initialization (__init__).

        TODO:
            Maybe redesign so it can be used as standalone method.
        """
        if os.path.exists(self.data_dir):
            if self.verbose:
                print('mnist data directory already exists, download aborted')
        else:
            if self.verbose:
                print('data directory does not exist, starting download...')
            # Create directories
            os.makedirs(self.data_dir)
            # Download each file and move it to given self.data_dir
            for file in self.files:
                request.urlretrieve(self.data_url + file, file)
                shutil.move(file, os.path.join(self.data_dir, file))
                if self.verbose:
                        print(file,'successfully downloaded')
            if self.verbose:
                print('... mnist data completely downloaded, enjoy.')

    def get_all_data(self, one_hot_enc=None, flatten=True, normalized=None):
        """Loads MNIST dataset into four numpy arrays.

        Default setup will return training and test images in a flat resprensentaion,
        meaning each image is row of 28*28 (784) pixel values. Labels are encoded as
        digit between 0 and 9. You can change both representation using the arguments,
        e.g., to preserve the image dimensions.
         
        Args:
            one_hot_enc (boolean): Indicates if labels returned in standard (0-9) or one-hot-encoded form
            flatten (boolean): Images will be returned as vector (flatten) or as matrix
            normalized (boolean): Indicates if pixels (0-253) will be normalized

        Returns:
            train_data (ndarray): A matrix containing training images
            train_labels (ndarray): A vector containing training labels
            test_data (ndarray): A matrix containing test images
            test_labels (ndarray): A vector containing test labels
        """
        train_images = self.get_images(os.path.join(self.data_dir,self.files[0]))
        train_labels = self.get_labels(os.path.join(self.data_dir,self.files[1]))
        test_images = self.get_images(os.path.join(self.data_dir,self.files[2]))
        test_labels = self.get_labels(os.path.join(self.data_dir,self.files[3]))

        if one_hot_enc:
            train_labels, test_labels = [self.to_one_hot_enc(labels) for labels in (train_labels, test_labels)]

        if flatten is False:
            train_images, test_images = [images.reshape(-1,28,28) for images in (train_images, test_images)]

        if normalized:
            train_images, test_images = [images/np.float32(256) for images in (train_images, test_images)]

        return train_images, train_labels, test_images, test_labels

    def get_images(self, file_path):
        """Unzips, reads and reshapes image files.

        Args:
            file_path (string): mnist image data file

        Returns:
            ndarray: A matrix containing flatten images
        """
        with gzip.open(file_path, 'rb') as file:
            images = np.frombuffer(file.read(), np.uint8, offset=16)
        return images.reshape(-1, 28 * 28)

    def get_labels(self, file_path):
        """Unzips and read label file.

        Args:
            file_path (string): mnist label data file

        Returns:
            ndarray: A vector containing labels
        """
        with gzip.open(file_path, 'rb') as file:
            labels = np.frombuffer(file.read(), np.uint8, offset=8)
        return labels


    def to_one_hot_enc(self, labels):
        """Converts standard MNIST label representation into an one-hot-encoding.

        Converts labels into a one-hot-encoding representation. It is done by
        manipulating a one diagonal matrix with fancy indexing.

        Args:
            labels (ndarray): Array of mnist labels

        Returns:
            ndarray: A matrix containing a one-hot-encoded label each row

        Example:
            [2,9,0] --> [[0,0,1,0,0,0,0,0,0,0]
                         [0,0,0,0,0,0,0,0,0,1]
                         [1,0,0,0,0,0,0,0,0,0]]
        """
        return np.eye(10)[labels]
