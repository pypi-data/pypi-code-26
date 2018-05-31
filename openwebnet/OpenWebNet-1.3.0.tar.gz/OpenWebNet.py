#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import logging

"""
Read Write class for OpenWebNet bus
"""
_LOGGER = logging.getLogger(__name__)


class OpenWebNet(object):

    #OK message from bus
    ACK = '*#*1##'
    #Non OK message from bus
    NACK = '*#*0##'
    #OpenWeb string for open a command session
    CMD_SESSION = '*99*0##'
    #OpenWeb string for open an event session
    EVENT_SESSION = '*99*1##'

    #Init metod
    def __init__(self,host,port,password):
        self._host = host
        self._port = int(port)
        self._psw = password
        self.risposta =[]
        self.light_risposta = dict()
        self.sensor_risposta = dict()
        self.sensor_SETrisposta = dict()
        self._session = False
        self._connection = False


    #Connection with host
    def connection(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host,self._port))
        self._connection = True

    #Close connection with host
    def disconnection(self):
        self._socket.close()
        self._connection = False
        self._session = False

    #Send data to host
    def send_data(self,data):
        #print('send_data ',data)
        #self._socket.send(data.encode())
        try:

            self._socket.send(data.encode())
            return True
        except:
            return False


    #Read data from host
    def read_data(self):
        try:
            message = str(self._socket.recv(1024).decode())
            #print('read data ',message)
            return message
        except:
            return "Broken"

#Calculate the password to start operation
    def calculated_psw (self, nonce):
        m_1 = 0xFFFFFFFF
        m_8 = 0xFFFFFFF8
        m_16 = 0xFFFFFFF0
        m_128 = 0xFFFFFF80
        m_16777216 = 0XFF000000
        flag = True
        num1 = 0
        num2 = 0
        self._psw = int(self._psw)

        for c in nonce:
            num1 = num1 & m_1
            num2 = num2 & m_1
            if c == '1':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_128
                num1 = num1 >> 7
                num2 = num2 << 25
                num1 = num1 + num2
                flag = False
            elif c == '2':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_16
                num1 = num1 >> 4
                num2 = num2 << 28
                num1 = num1 + num2
                flag = False
            elif c == '3':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & m_8
                num1 = num1 >> 3
                num2 = num2 << 29
                num1 = num1 + num2
                flag = False
            elif c == '4':
                length = not flag

                if not length:
                    num2 = self._psw
                num1 = num2 << 1
                num2 = num2 >> 31
                num1 = num1 + num2
                flag = False
            elif c == '5':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 5
                num2 = num2 >> 27
                num1 = num1 + num2
                flag = False
            elif c == '6':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 << 12
                num2 = num2 >> 20
                num1 = num1 + num2
                flag = False
            elif c == '7':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFF00
                num1 = num1 + (( num2 & 0xFF ) << 24 )
                num1 = num1 + (( num2 & 0xFF0000 ) >> 16 )
                num2 = ( num2 & m_16777216 ) >> 8
                num1 = num1 + num2
                flag = False
            elif c == '8':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = num2 & 0xFFFF
                num1 = num1 << 16
                num1 = num1 + ( num2 >> 24 )
                num2 = num2 & 0xFF0000
                num2 = num2 >> 8
                num1 = num1 + num2
                flag = False
            elif c == '9':
                length = not flag
                if not length:
                    num2 = self._psw
                num1 = ~num2
                flag = False
            else:
                num1 = num2
            num2 = num1
        return num1 & m_1

    #Open command session
    def cmd_session(self):
        #create the connection
        if  not self._connection:
            self.connection()

        #if the bus answer with a NACK report the error
        if self.read_data() == OpenWebNet.NACK :
            _LOGGER.exception("Non posso inizializzare la comunicazione con il gateway")

        #open commanc session
        self.send_data(OpenWebNet.CMD_SESSION)

        answer = self.read_data()
        #if the bus answer with a NACK report the error
        if answer == OpenWebNet.NACK:
            _LOGGER.exception("Il gateway rifiuta la sessione comandi")
            return False

        #calculate the psw
        psw_open = '*#' + str(self.calculated_psw(answer)) + '##'

        #send the password
        self.send_data(psw_open)

        #if the bus answer with a NACK report the error
        if self.read_data() == OpenWebNet.NACK:
             _LOGGER.exception("Password errata")

        #othefwise set the variable to True
        else:
            self._session = True
            #print('cmd_session')

    def extractor (self,answer,where):
        #Se la risposta è luci
        #print('answer 2 e 7',answer[2],answer[7:9])
        if answer[1] == '1':
            adic = dict()
            adic['who']='1'
            adic['what']=answer[3]
            adic['where']=answer[5:7]
            #print('adic1',adic)
            self.light_risposta[answer[5:7]]=answer[3]
            print('light_risposta', self.light_risposta)
            #self.crearisposta(adic)

        elif answer[2] == '4'and answer[7]=='0':
            adic = dict()
            adic['who']='4'
            adic['where']=answer[4:4+len(where)]
            adic['set']='0'
            adic['valore']=answer[7+len(where):11+len(where)]
            #print('adic2',adic)
            self.sensor_risposta[answer[4:4+len(where)]]=answer[7+len(where):11+len(where)]
            print('sensor_risposta',self.sensor_risposta)
            #self.crearisposta(adic)

        elif answer[2] == '4' and answer[5+len(where):7+len(where)] == '14':
            adic = dict()
            adic['who']='4'
            adic['where']=answer[4:4+len(where)]
            adic['set']='14'
            adic['valore']=answer[8+len(where):12+len(where)]
            #print('adic3',adic)
            self.sensor_SETrisposta[answer[4:4+len(where)]]=answer[8+len(where):12+len(where)]
            print('sensor_SETrisposta',self.sensor_SETrisposta)
            #self.crearisposta(adic)



    #def crearisposta(self,adic):
#        print('adic',adic)
#        if self.risposta ==[]:
#            self.risposta.append(adic)
#            print('era vuoto lo creo', self.risposta)
#        else:
#            if adic['who']=='4':
#                found='0'
#                for i in range(len(self.risposta)):
#                    if self.risposta[i]['who']==adic['who'] and self.risposta[i]['where']==adic['where'] and self.risposta[i]['set']==adic['set']:
#                        self.risposta[i]=adic
#                        found='1'
#                if found=='0':
#                     self.risposta.append(adic)
#                print('appendo la grandezza',self.risposta)
#            elif adic['who']=='1':
#                found='0'
#                for i in range(len(self.risposta)):
#                    if self.risposta[i]['who']==adic['who'] and self.risposta[i]['where']==adic['where']:
#                        self.risposta[i]=adic
#                        found='1'
#                if found=='0':
#                    self.risposta.append(adic)
#                print('appendo lo stato', self.risposta)






    #Check that bus send al the data
    def check_answer (self,message):
        #if final part of the message is not and ACK or NACK
        end_message = ''
        #print('message ricevuto da check answer', message)
        #print('OpenWebNet.ACK',OpenWebNet.ACK)
        if message[len(message)- 6:] != OpenWebNet.ACK and message[len(message)- 6:] != OpenWebNet.NACK:
            #the answer is not completed, read again from bus
            #print('message -len',message[len(message)-6:])
            end_message = self.read_data()
            #add it

            #print('message +end message',message + end_message)
            return message + end_message

        #check if I get a NACK
        if message[len(message)- 6:] == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")


        return message


    #Normal request to BUS
    def normal_request(self,who,where,what):

        print('normal_request', who,where,what)
        #if the command session is not active
        if not self._session:
            self.cmd_session()

        #prepare the request
        normal_request = '*' + who + '*' + what + '*' + where + '##'

        #and send
        if not self.send_data(normal_request):
            self.disconnection()
            self.normal_request(who,where,what)
        #read the answer

        message = self.read_data()


        if message == "Broken":

            self.disconnection()
            self.normal_request(who,where,what)
        #read the answer

        if message == OpenWebNet.ACK:
            return True
        #check if I get a NACK
        if message == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")
            return False


    #Request of state of a components on the bus
    def stato_request(self,who,where,what):
        print('stato request', who,where,what)
        #if the command session is not active
        if not self._session:
            self.cmd_session()

        #preparo la richiesta property
        #stato LUCE
        if who == '1':
            request = '*#' + who + '*' + where + '##'
        #stato sonda T
        elif who == '4':
            request = '*#' + who + '*' + where + '*' + what + '##'

        #e la Invio
        if not self.send_data(request):
            self.disconnection()
            self.stato_request(who,where)

        #risposta dal bus
        message = self.read_data()


        if message == "Broken":

            self.disconnection()
            self.stato_request(who,where)
        #e leggo la risposta

        #verifico se il bus ha trasmesso tutti i dati
        check_message = self.check_answer(message)

        if message[len(message)- 6:] == OpenWebNet.NACK:
            _LOGGER.exception("Errore Comando non effettuato")
        #o un ACK
        else:
            self.extractor(check_message,where)



    #Scrittura di una grandezza
    def grandezza_write(self,who,where,grandezza,valori):
        #Se non è attiva apro sessione comandi
        if not self._session:
            self.cmd_session()

        #preparo la richiesta
        val =''
        for item in valori:
            val = '*' + val[item]

        grandezza_write = '*#' + who + '*' + where + '*#' + grandezza + val + '##'

        #e la Invio
        try:

            self.send_data(grandezza_write)

        except:

            self.disconnection()
            self.grandezza_write(who,where,grandezza,valori)

        #e leggo la risposta
        message = self.read_data()

        #if there is some problems on the socket
        if message=='':
            #close it
            self.disconnection()
            #and repeat
            self.grandezza_write(who,where,grandezza,valori)
        #e la Invio


        #e leggo la risposta
        return message

    def stato_answer(self,who,where,set):
        if who == '1':
            return self.light_risposta[where]
        elif who == '4' and set == '0':
            return self.sensor_risposta[where]
        elif who == '4' and set == '14':
            return self.sensor_SETrisposta[where]
        return '0'


    #metodo che invia il comando di accensione della luce where sul bus
    def luce_on (self,where):
        if self.normal_request('1',where,'1'):
            self.light_risposta[where] = '1'
        else:
            self.light_risposta[where] = '0'


    #metodo che invia il comandi di spegnimento della luce where sul bus
    def luce_off(self,where):
        if self.normal_request('1',where,'0'):
            self.light_risposta[where] = '0'
        else:
            self.light_risposta[where] = '1'

    #metodo per la richiesta dello stato della luce where sul bus
    def ask_stato_luce(self,where):
        #print('stato_luce')
        self.stato_request('1',where,'0')



    #Metodo per la lettura della temperatura
    def ask_read_temperature(self,where):
        #print('lettura temperatura')
        self.stato_request('4',where,'0')


    #Metodo per la lettura della temperatura settata  nella sonda
    def ask_read_setTemperature(self,where):
        #print('lettura set temperature')
        self.stato_request('4',where,'14')


    #Metodo per la lettura dello stato della elettrovalvola
    def ask_read_sondaStatus(self,where):
        #print('lettura stato sonda temperature')
        self.stato_request('4',where,'19')

    def answ_stato_luce(self,where):
        stato = self.stato_answer('1',where,'1')
        if stato=='1':
            return True
        else:
            return False

    def answ_read_temperature(self,where):
        valore = float(self.stato_answer('4',where,'0'))/10
        return valore

    def answ_read_setTemperature(self,where):
        setvalore = float(self.stato_answer('4',where,'14'))/10
        return setvalore
