'''
Created on 17 de mai de 2018

@author: koliveirab
''' 
from Pyautomators.Pywebautomator import Web
from Pyautomators import Pyambautomator 
''' Abrindo o driver'''
browser=Web("Chrome",Pyambautomator.path_atual())

browser.pagina("https://code.tutsplus.com/categories/python?page=6")
print(browser.titulo())
browser.maximiza()
browser.print_janela("teste_novo.png")
browser.fechar_programa()