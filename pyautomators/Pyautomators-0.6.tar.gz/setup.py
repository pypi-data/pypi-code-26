# -*- coding: utf-8 -*-
from setuptools import setup,find_packages

setup(name='Pyautomators',
      version='0.6',
      url='https://github.com/kauebonfimm/Pyautomator',
      license='MIT',
      author='KaueBonfim',
      author_email='kaueoliveir95@hotmail.com',
      description='Biblioteca de automação para geracao completa de ambientacao de testes',
      packages=['Pyautomators'],
	  install_requires=["pytesseract","pillow","pyautogui","assertpy","cx_Oracle","selenium","pytractor","numpy","mysqlclient","opencv-python","Appium-Python-Client","pynput","behave2cucumber","python-jenkins","behave","django","pandas"],
      zip_safe=True)