'''
@author: KaueBonfim
'''

import json
import pytesseract as ocr
from PIL import Image
import pyautogui
import numpy
import pandas
def imagem_para_caracter(imagem:str):
    imagem=imagem.replace("\\", "/")
    im=Image.open(imagem)
    return ocr.image_to_string(im,lang='eng')

def pegarConteudo(NomeArquivo,leitura=None):
    arquivo = open(NomeArquivo, 'r')
    if(leitura==None):
        lista = arquivo.read()
    elif(leitura=="linha"):
        lista=arquivo.readlines()
    arquivo.close()
    return lista

def receber_texto_usuario(descricao):
    return pyautogui.prompt(text=descricao, title='prompt' , default='')

def tela_texto(xi:int, yi:int, xf:int, yf:int,path_arquivo,y=100,x=500)->str:
    result=lambda a,b:b-a 
    xd=result(xi,xf)
    yd=result(yi,yf)
    nome=path_arquivo.replace("\\", "/")
    xd=xf-xi
    yd=yf-yi
    print(xi,yi,xd,yd)
    pyautogui.screenshot(nome,region=(xi,yi,xd,yd))
    im = Image.open(nome)
    ims=im.resize((x, y),Image.ANTIALIAS)
    ims.save(nome,'png')
    im=Image.open(nome)
    return ocr.image_to_string(im,lang='eng')

def alinharImagem(imagem,x,y):
    im = Image.open(imagem)
    ims=im.resize((x, y),Image.ANTIALIAS)
    ims.save(imagem,'png')
    
def pegarConteudoJson(NomeArquivo):
    arquivo = open(NomeArquivo, 'r')
    lista = arquivo.read()
    arquivo.close()    
    listat=json.loads(lista)    
    return listat

def pegarConteudoCSV(NomeArquivo:str):
    valor=pandas.read_csv(NomeArquivo)
    pandas.DataFrame(valor)
    return valor