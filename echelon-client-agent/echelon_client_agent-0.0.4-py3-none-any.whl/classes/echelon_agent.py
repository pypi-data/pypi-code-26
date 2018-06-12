# -*- coding: utf-8 -*-

from utils.db import (
    get_engine,
    DbCredentials,
    set_config_db,
)
from classes.echelon_client_factory import EchelonClientFactory
from twisted.internet import reactor


class EchelonAgent:
    connection_field = ''
    server_field = ''
    sql_lector_field = ''

    def __init__(self):
        self.db_cred = DbCredentials()
        self.factory = EchelonClientFactory()

    def set_values(self, **data):
        self.conexion_field = data['echelon_db']
        self.server_field = data['echelon_server_receptor']
        self.sql_lector_field = data['echelon_sql_lector']
        self.echelon_lapse_seconds = data['echelon_lapse_seconds']

    def check_require_fields(self):
        if(self.conexion_field == "" or self.server_field == "" or
                self.sql_lector_field == ""):
            return False

        return True

    def send_query(self, table='', id_name='', field=''):
        if self.check_require_fields():
            is_correct, engine, user, password, host, port, name_db = (
                self.db_cred.check_string_con(self.conexion_field)
            )

            print(
                "engine, user, password, host, port, name_db: ",
                engine, user, password, host, port, name_db
            )

            if is_correct:
                self.db_values = set_config_db(**{
                    'engine': engine,
                    'name': name_db,
                    'host': host,
                    'user': user,
                    'pass': password,
                    'port': port,
                })
                self.engine, self.session = get_engine(self.db_values)
                print("... Conectado a Base de Datos local\n")
            else:
                print("Error")

            is_correct, host, port = self.db_cred.check_host_port_receptor(
                self.server_field)
            if is_correct:
                self.factory.set_data(
                    self.sql_lector_field, self.engine, table, id_name, field)
                self.factory.set_lapse_time(self.echelon_lapse_seconds)
                reactor.connectTCP(host, int(port), self.factory)
                reactor.run()
            else:
                print("Error")

        else:
            print("Error")
