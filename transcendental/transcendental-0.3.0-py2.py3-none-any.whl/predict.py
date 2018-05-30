import argparse
import os.path
from keras.models import model_from_yaml
from keras.models import Sequential
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import numpy as np


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
    yaml_file = open('/etc/transcendental/models/model.yaml', 'r')
    loaded_model_yaml = yaml_file.read()
    yaml_file.close()
    classifier = model_from_yaml(loaded_model_yaml)
    # load weights into new model
    classifier.load_weights("models/model.h5")
    print("Loaded model from disk")

    train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)
    training_set = train_datagen.flow_from_directory(
        'CNN_Data/training_set',
        target_size=(64, 64),
        batch_size=32,
        class_mode='binary')

    # Predict with the model
    test_image = image.load_img(args.image, target_size = (64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    result = classifier.predict(test_image)
    training_set.class_indices
    prediction = "unknown"
    if result[0][0] == 1:
        prediction = 'dog'
    else:
        prediction = 'cat'
    print("It's a {}".format(prediction))


if __name__ == "__main__":
    main()
