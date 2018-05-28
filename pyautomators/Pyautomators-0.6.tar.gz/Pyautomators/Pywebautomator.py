'''

@author: KaueBonfim
'''
import os 
from pytractor import webdriver as web
from selenium import webdriver
from Pyautomators.Pyelementautomator import Pyelement
from Pyautomators.Pykeymouseautomator import Pykeymouseautomator
from selenium.webdriver import ActionChains,common


class Web(Pyelement,Pykeymouseautomator):
    def __init__(self,driver,path_driver=""):
        if(driver == 'Chrome'):
            self.driver=webdriver.Chrome(str(path_driver)+"chromedriver.exe")
            
            
        elif(driver == 'Firefox'):            
            self.driver=webdriver.Firefox(str(path_driver)+"geckodriver.exe")
            
            
        elif(driver == 'Ie'):             
            self.driver=webdriver.Ie(str(path_driver)+"IEDriverServer.exe")
            
        self.acoes=ActionChains(self.driver)
        self.alerta=common.alert.Alert(self.driver)
    
    def fechar_programa(self):
        self.driver.quit()
        
        
    def url_atual(self):
        return self.driver.current_url
        
    def pagina(self,url):
        self.driver.get(url)
        
    def maximiza(self):
        self.driver.maximize_window()
        
    def atualizar(self):
        self.driver.refresh()
        
    def voltar(self):
        self.driver.back()
    
    def limpar(self):
        self.driver.clear()
        
    def pegar_atributo(self,info):
        self.driver.get_attribute(info)
        
    def titulo(self):
        return self.driver.title
    
    def navegador(self):
        return self.driver.name
    
    def clica_mouse_elemento(self,elemento=None,tipo=None,botao=None):
        element=self.elemento(elemento,tipo) 
        if(botao=="direito"):
            self.acoes.context_click(element)
        elif(botao=="esquerdo"):
            self.acoes.click_and_hold(element)
        else:
            self.acoes.click(element)
        
    def arrastar_elemento(self,elemento1_tipo:tuple,elemento2_tipo:tuple):
        elemento1=self.elemento(elemento1_tipo[0],elemento1_tipo[1])
        elemento2=self.elemento(elemento2_tipo[0],elemento2_tipo[1])
        self.acoes.drag_and_drop(elemento1, elemento2)
        
    def arrastar_elemento_lista(self,elemento1_tipo_indice:tuple,elemento2_tipo_indice:tuple):
        elemento1=self.elementos_list(elemento1_tipo_indice[0],elemento1_tipo_indice[1],elemento1_tipo_indice[2])
        elemento2=self.elementos_list(elemento2_tipo_indice[0],elemento2_tipo_indice[1],elemento2_tipo_indice[2])
        self.acoes.drag_and_drop(elemento1, elemento2)
        
    def popUp_aceitar(self,aceitar:bool):
        if(aceitar==True):
            self.alerta.accept()
        elif(aceitar==False):
            self.alerta.dismiss()
        
    def popUp_autenticar(self,usuario,senha):
        self.alerta.authenticate(usuario,senha)
        
    def popUp_escrever(self,texto):
        self.alerta.send_keys(texto)
        
    def popUp_pegar_texto(self):
        return self.alerta.text
    
    def print_janela(self,path_imagem):
        self.driver.save_screenshot(path_imagem)