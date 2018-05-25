'''

@author: KaueBonfim
'''
import os
import re
import sqlite3

class Project(object):
    '''
    classdocs
    '''

    @staticmethod
    def Criar_Projeto(nome_projeto,diretorio=None):
        
        if(diretorio!=None):
            os.chdir(diretorio)
        
        os.mkdir(nome_projeto)
        
        os.chdir(nome_projeto)
        
        
        lista_pastas_principal=["dados","docs","drivers","elementosImagem","features","lib","steps","tools","steps/unit_test","steps/models","features/reports"]
        for lin in lista_pastas_principal:
            os.mkdir(lin)
            
        text=open("__init__.py","w")
        text.close()
                
        text=open("tools/__init__.py","w")
        text.close()
        
        text=open("environment.py","w")
        text.writelines('\n"""\t\tPyautomators Framework de teste \n\n\t\t\t{}"""\n\n'.format(nome_projeto))
        text.writelines('from Pyautomators import *\nfrom time import sleep\n')
        text.writelines("def before_all(context):\n\tpass\n\n")
        text.writelines("def before_features(context,feature):\n\tpass\n\n")
        text.writelines("def before_scenario(context,scenario):\n\tpass\n\n")
        text.writelines("def before_steps(context,step):\n\tpass\n\n")
        text.writelines("def after_steps(context,step):\n\tpass\n\n")
        text.writelines("def after_scenario(context,scenario):\n\tpass\n\n")
        text.writelines("def after_feature(context,feature):\n\tpass\n\n")
        text.writelines("def after_all(context):\n\tpass\n\n")
        text.close()
                
        text=open("features/behave.ini","w")
        text.writelines("[behave]\njunit=True\njunit_directory=./reports\nformat=json.pretty\noutfiles =./reports/test.json\nstdout_capture=True\nlog_capture=True\n")
        text.close
        
        text=open("steps/__init__.py","w")
        text.close()
        
        text=open("steps/models/__init__.py","w")
        text.close()
        
        text=open("steps/unit_test/__init__.py","w")
        text.close()
        
        text=open("lib/requerimento","w")
        text.writelines("Pyautomators")
        text.close()
        bank=sqlite3.connect("dados/bank.db")
        bank.close()    
     
    @staticmethod
    def criar_medotos(diretorio_features:str):
        lista_de_features=[]
        dicionario_de_steps=[]
        lista_metodo=[]
        
        os.chdir(diretorio_features)
        path=os.getcwd()
        path=str(path).replace("\\", "/")
        #os.chdir(path+"/features")
        os.chdir("features")
        """ Lista de features na pasta"""
        pasta=os.listdir()
        for lista in pasta:
            valor=re.search(".feature",str(lista))
            if(valor!=None):
                lista_de_features.append(lista)
                
                
       
        
        """ Iterador de features"""
        for lin in lista_de_features:
            """ Iterador de Steps"""
            step=open(lin,"r+")
            valor=step.readlines()
            """ Iterador de linhas"""
            for valo in valor:
                """ Lista de valores para pesquisar padrao"""
                list=["Given","When","Then","And","But"]
                
                """ Iterador de valores de pesquisa"""
                for l in list:
                    valor=re.search(l,valo)
                    """ Tratamento se o valor for encontrado"""
                    if(valor!=  None):
                        
                        
                        listass=str(l).replace("Given","given").replace("When","when").replace("Then","then").replace("And","{}".format("and")).replace("\n", "")
                        valorreal=str(valo).replace("\t","").replace("\n", "").replace("Given","").replace("When","").replace("Then","").replace("And","").replace("<","{").replace(">","}")
                        
                        dicionario_de_steps.append([listass,valorreal[1:]])
                        
         
        
        """ Gerar metodos"""
        ultimo_step=None
        for step in dicionario_de_steps:
            context=""
            if(step[0]=="and"):
                step[0]=ultimo_step
            valor1=str(step[1]).find("{")
            valor2=str(step[1]).find("}")
            if(valor1!=-1):
                data=step[1]
                context=",{}".format(data[int(valor1+1):int(valor2)])
            value="@{}('{}')\ndef step_implement(context{}):\n\tpass".format(step[0],step[1],context)
            lista_metodo.append(value)
            #print("@{}('{}')\ndef step_implement(context{}):\n\tpass".format(step[0],step[1],context))
            ultimo_step=step[0]
                  
        ''' Gerar arquivo'''
            
        os.chdir(path+"/steps")
           
        
        text=open("steps_implement.py","w")
        text.writelines("\n'''\t\t Implementacao de steps'''\n\nfrom behave import *\nfrom time import sleep\n\n")
        for ls in lista_metodo:
            text.seek(0,2)
            print(ls)
            text.writelines(ls+"\n\n\n")
        text.close()