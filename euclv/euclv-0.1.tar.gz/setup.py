from setuptools import setup

setup(name='euclv',
      version='0.1',
      description='Face emotion detection for affective computing',
      url='https://github.com/g-soto/uclvfeel.git',
      author='GG',
      author_email='gsoto@uclv.cu',
      license='GPL',
      packages=['euclv'],
	  install_requires=['markdown','opencv-contrib-python','dlib','sklearn','numpy'],
include_package_data=True,
      zip_safe=True)
