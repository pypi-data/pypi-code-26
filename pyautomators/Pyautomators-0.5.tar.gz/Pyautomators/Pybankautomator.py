import MySQLdb
import cx_Oracle
import sqlite3

class PyDatas():
    
    def __init__(self,Servidor,user=None,senha=None,banco=None,endereco=None,porta=None):
        if (Servidor=="MySQL"):
            self.__bank=MySQLdb.connect(user=user,passwd=senha,db=banco,host=endereco,port=porta,autocommit=True)
            
        elif (Servidor=="Oracle"):
            self.__bank=cx_Oracle.connect('{}/{}@{}{}'.format(user,senha,endereco,porta))
            
        elif(Servidor=="SQLite"):
            self.__bank=sqlite3.connect(banco)
            
        self.cursor=self.__bank.cursor()
        
    def buscar_tudo(self,query:str):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def buscar_um(self,query:str):
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def inserir_lista(self,sql:str,valores:list):
        self.cursor.executemany(sql,valores)
        self.__bank.commit()
    
    def inserir(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
    
    def deletar(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
    
    def atualizar(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
        
    def fechar_conexao(self):
        self.cursor.close()
        self.__bank.close()