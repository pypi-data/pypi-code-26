'''

@author: KaueBonfim
'''
import pyautogui

from pynput.mouse import Listener

def tamanhoTela():
    return pyautogui.size()

def pegar_clique():
    def on_click(x, y, button, pressed):
        print('{0} em {1}'.format('Up ' if  pressed else 'Down ',(x, y)))
    with Listener(on_click=on_click) as listener:
        listener.join()
