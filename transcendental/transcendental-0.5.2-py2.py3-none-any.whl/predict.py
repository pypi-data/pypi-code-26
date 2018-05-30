import argparse
import os.path
from keras.models import model_from_yaml
from keras.models import Sequential
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import config


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error('The file {} does not exist!'.format(arg))
    return arg


def argparser():
    parser = argparse.ArgumentParser(description='Recognize cat and dogs')
    parser.add_argument('image', help='an image to analyze',
        type=lambda x: is_valid_file(parser, x))
    return parser.parse_args()


def main():
    args = argparser()
    # load YAML and create model
    yaml_file = open('{}/model.yaml'.format(config.MODELS), 'r')
    loaded_model_yaml = yaml_file.read()
    yaml_file.close()
    classifier = model_from_yaml(loaded_model_yaml)
    # load weights into new model
    classifier.load_weights("{}/model.h5".format(config.MODELS))
    print("Loaded model from disk")

    # Predict with the model
    test_image = image.load_img(args.image, target_size = (64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    result = classifier.predict(test_image)
    prediction = "unknown"
    if result[0][0] == 1:
        prediction = 'dog'
    else:
        prediction = 'cat'
    print("It's a {}".format(prediction))


if __name__ == "__main__":
    main()
