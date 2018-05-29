'''

@author: KaueBonfim
'''
import pyautogui

from pynput.mouse import Listener
from pynput import keyboard

def tamanhoTela():
    return pyautogui.size()

def pegar_clique():
    
    def on_click(x, y, button, pressed):
        print('{0}{1}'.format('' if  pressed else '',(x, y)))
    
    with Listener(on_click=on_click) as listener:
        listener.join()
    


def localizacao_imagem(imagem):  
    return pyautogui.locateOnScreen(imagem)

def localizacao_centro_imagem(imagem):
    return pyautogui.locateCenterOnScreen(imagem)

def localiza_todas_imagens(imagem):
    return list(pyautogui.locateAllOnScreen(imagem))
