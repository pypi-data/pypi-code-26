'''

@author: KaueBonfim
'''

import pyautogui
from  assertpy import assert_that


def verifica_tela(path_imagem:str)->bool:
    if(pyautogui.locateOnScreen(image=path_imagem)):
        return True
    else:
        return False
    
def verifica_valor(valor,tipo,comparado=None)->bool:
    retorno="Inserir um tipo correto"
    if(tipo=="igual"):
        retorno=assert_that(valor).is_equal_to(comparado)
    elif(tipo=="verdadeiro"):
        retorno=assert_that(valor).is_true()
    elif(tipo=="diferente"):
        retorno=assert_that(valor).is_not_equal_to(comparado)
    elif(tipo=="falso"):
        retorno=assert_that(valor).is_false()
    elif(tipo=="contem"):
        retorno=assert_that(valor).contains(comparado)
    
    return retorno