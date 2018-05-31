from distutils.core import setup
import os,qscan.__init__
from glob import glob

def get_data_names(root):
    '''
    Return list of all filenames (not directories) under root.
    '''
    temp = [root+'/*']
    for dirpath, dirnames, filenames in os.walk(root):
        temp.extend((os.path.join(dirpath, d, '*') for d in dirnames))
    names = []
    for path in temp:
        if any(os.path.isfile(f) for f in glob(path)):
            names.append(path.replace('qscan/',''))
    return names

package_data = {'qscan' : get_data_names('qscan/data')}

setup(
    name="qscan",
    version=qscan.__version__,
    author="Vincent Dumont",
    author_email="vincentdumont@gmail.com",
    packages=["qscan"],
    requires=["numpy","matplotlib","scipy","astropy"],
    package_data = package_data,
    include_package_data=True,
    scripts = glob('scripts/*'),
    url="https://astroquasar.gitlab.io/qscan/",
    description="Quasar spectra scanner",
    install_requires=[]
)
