'''
Module to handle IN operations
'''

import re
import socket

class INTelecom():
    '''INTelecom object'''

    def __init__(self, host, username, password, port, buffer_size):
        '''Initializes the INConnection setting the host and port'''
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.in_socket.connect((self.host, self.port))
        self.username = username
        self.password = password
        self.session_id = ''

    def __enter__(self):
        self.login()
        return self

    def login(self):
        '''Login to IN server'''
        response = self.execute_login_command('login|{0}|{1}'.format(self.username, self.password))

        success_finder = re.compile(r'succeeded', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            session_id_collector = re.compile(r'ACKLGN(?P<SESSION>[0-9]{8})', re.IGNORECASE)
            self.session_id = session_id_collector.findall('{}'.format(response))[0]
        else:
            raise RuntimeError('IN login failed')

    def logout(self):
        '''Logout of the IN session'''
        response = self.execute_command('logout|{0}'.format(self.username))

        success_finder = re.compile(r'succeeded', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            print('Logged out of session ID:', self.session_id, 'successfully')
        else:
            print('Logout of session ID:', self.session_id, 'failed')

    def reset_sim_password(self, msisdn, sim_password):
        '''Reset password'''
        response = self.execute_command('MODI EPPC SIMPSWD:MSISDN={0},OPRPSWD={1},NEWPSWD={2},CFMPSWD={2};'.format(msisdn, self.password, sim_password))

        success_finder = re.compile(r'RETN=0', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            # TODO: Replace with logging
            return True
        else:
            # TODO: Replace with logging
            return False

    def purchase_package(self, msisdn, package_type, package_grade, sim_password):
        '''Purchase package'''

        # Reset SIM password.
        if self.reset_sim_password(msisdn, sim_password):
            # Purchase the package.
            response = self.execute_command('SET EPPC RESPKG:MSISDN={0},MSUBPSWD={1},PKGTYPE={2},PKGGRADE={3};'.format(msisdn, sim_password, package_type, package_grade))

            success_finder = re.compile(r'RETN=0', re.IGNORECASE)

            if success_finder.search('{}'.format(response)):
                # TODO: Replace with logging
                return True
            else:
                # TODO: Replace with logging
                return False
        else:
            return False

    def change_profile(self, msisdn, profile):
        '''Change account profile'''

        response = self.execute_command('MODI EPPC USERTYPE:MSISDN={0},USERTYPE={1};'.format(msisdn, profile))

        success_finder = re.compile(r'RETN=0', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            # TODO: Replace with logging
            return True
        else:
            # TODO: Replace with logging
            return False

    def display_account_info(self, msisdn):
        '''Display account info'''
        response = self.execute_command('DISP EPPC ACNTINFO:MSISDN={0},QUERYTYPE=1,QUERYSCP=1;'.format(msisdn))

        result_finder = re.compile(r'RESULT=".*"')
        values = re.split('=|"| & ', result_finder.findall(str(response))[0])[2:31]
        keys = ['MSISDN', 'ACCLEFT', 'LOCKFLG', 'ACNTSTAT', 'CLMFLG', 'CALLINGROAMOUTFLG', 'CALLEDROAMOUTFLG', 'CLIALW', 'OCSFLG', 'CALLRANGE', 'SERVICESTART', 'ACCOUNTSTOP', 'CALLSERVSTOP', 'PREACCOUNTSTOP', 'PREFREEZESTOP', 'USERTYPE', 'SUBSCRIBERTYPE', 'USERFLG', 'LANGUAGE', 'SMLANGUAGE', 'LIFECIRCLE', 'MSFEE', 'MSTOTALFEE', 'MSMONTHDEDUCT', 'BIRTHDAY', 'ENTRYBLACKTIME', 'DIALMOBILENUMFLG', 'ANSCLCTCALLFLG', 'TMPNUMFLG']

        account_info = zip(keys, values)

        return account_info

    def credit_account(self, msisdn, amount, reason):
        '''Credit account'''
        
        response = self.execute_command('MODI EPPC ACCOUNT:MSISDN={0},BALANCE={1},APPINFO={2};'.format(msisdn, amount, reason))

        success_finder = re.compile(r'RETN=0', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            # TODO: Replace with logging
            return True
        else:
            # TODO: Replace with logging
            return False

    def debit_account(self, msisdn, amount, reason):
        '''Debit account'''

        response = self.execute_command('MODI EPPC ACCOUNT:MSISDN={0},BALANCE=-{1},APPINFO={2};'.format(msisdn, amount, reason))

        success_finder = re.compile(r'RETN=0', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            # TODO: Replace with logging
            return True
        else:
            # TODO: Replace with logging
            return False

    def scratch_card_recharge(self, msisdn, recharge_code, reason):
        '''Recharge using scratch card'''
        response = self.execute_command('CARD EPPC ACNT: MSISDN={0},PPCCARDPIN={1},APPINFO={2}'.format(msisdn, recharge_code, reason))
        success_finder = re.compile(r'RETN=0', re.IGNORECASE)

        if success_finder.search('{}'.format(response)):
            # TODO: Replace with logging
            return True
        else:
            # TODO: Replace with logging
            return False

    def execute_command(self, command):
        '''Execute commands'''

        formatted_command = '{0}|{1}\r\n'.format(self.session_id, command)
        self.in_socket.send(formatted_command.encode())
        response = self.in_socket.recv(self.buffer_size)

        return response

    def execute_login_command(self, command):
        '''Execute login command'''

        formatted_command = '{0}\r\n'.format(command)
        self.in_socket.send(formatted_command.encode())
        response = self.in_socket.recv(self.buffer_size)

        return response

    def __exit__(self, exc_type, exc_value, traceback):
        '''Destructor'''
        self.logout()
        self.in_socket.close()
