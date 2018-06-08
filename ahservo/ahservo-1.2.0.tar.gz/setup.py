import setuptools

setuptools.setup(
        name = 'ahservo',
        version = '1.2.0',
        packages = setuptools.find_packages(),
        author = 'sashankMNS',
        license = 'MIT',
        install_requires = ['Adafruit_PCA9685',],
        description = 'Updated version with maximum and minimum values',
)
        
