from setuptools import setup,find_packages

setup(name='trueface',
      version='0.1',
      description='Trueface Face Recognitoin',
      url='https://github.com/getchui/truefacesdk',
      author='Nezare Chafni',
      author_email='nchafni@truface.ai',
      license='MIT',
      packages=['trueface'],
      package_data={'trueface': ['model/*json', 'model/*caffemodel', 'model/*prototxt','model/*params','logo.png']},
      install_requires=[
                'pubnub',
                'imutils',
                'opencv-python',
                'mxnet',
                'dlib',
                'requests',
                'requests_futures',
                'mss',
                'art',
                'numpy',
                'pandas'
            ],
      entry_points={
       'console_scripts': [
           'trueface = trueface.trueface:main',
           'enroll = trueface.enroll:main',
       ],
      },
      zip_safe=False)