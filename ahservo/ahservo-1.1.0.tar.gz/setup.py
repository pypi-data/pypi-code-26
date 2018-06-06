import setuptools

setuptools.setup(
        name = 'ahservo',
        version = '1.1.0',
        packages = setuptools.find_packages(),
        author = 'sashankMNS',
        license = 'MIT',
        install_requires = ['Adafruit_PCA9685',],
        description = 'Control servo with an angle between 0 and 180 degrees',
)
        

