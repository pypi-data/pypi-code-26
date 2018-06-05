#*- coding: utf-8 -*-
import os
from jenkins import Jenkins
import jenkins

class repoJenkis():
    def __init__(self):
        self.jenkins_server=None
        
    def conectar_jenkins(self,url,senha_user,nome_user):
        self.jenkins_server= Jenkins(url,nome_user, senha_user)
    
    def construir_no_jenkins(self,nome):
        self.jenkins_server.build_job(nome)
    
def iniciar_repo(diretorio=None,nome=None,email=None):
   
    if(diretorio!=None):
        os.chdir(diretorio)
    os.system("git init")
    if(nome!=None):
        os.system('git config --local user.name %s'% nome)
    if(email!=None):
        os.system('git config --local user.email "%s"'% email)
    
    

def add_repo(arquivos="*"):
    for list in arquivos:
        os.system("git add %s" % list)
    
def commit(menssagem):
    os.system('git commit -m "%s"'% menssagem)

def enviar_github(url):
    os.system("git remote add origem %s"% url)
    os.system("git push -f origem master")

def proxy_git(url,usuario,senha):
    os.system('git config --local http.proxy http://{}:{}@{}.git'.format(usuario,senha,url))
    os.system('git config --local https.proxy https://{}:{}@{}.git'.format(usuario,senha,url))
    
