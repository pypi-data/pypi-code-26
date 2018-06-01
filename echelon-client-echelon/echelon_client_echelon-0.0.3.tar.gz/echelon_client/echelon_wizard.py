# -*- coding: utf-8 -*-
from classes.echelon_agent import EchelonAgent
from classes.echelon_console import EchelonConsole


def two_steps(wizard, option):

    while option != '3':
        if option == "1":
            wizard.show_conf_step()
            option_conf = wizard.show_sub_menu()
            option_conf = wizard.wait_editable_option(option_conf)

            while option_conf == 'e':
                option_conf = wizard.inside_conf()

            if option_conf == 'g':
                # wizard.save_conf()
                option = wizard.show_main_menu()
            if option_conf == 's':
                option = wizard.show_main_menu()

        if option == "2":
            wizard.show_sql_step()
            option_sql = wizard.show_sub_menu()
            option_sql = wizard.wait_editable_option(option_sql)

            while option_sql == 'e':
                option_sql = wizard.inside_sql()

            if option_sql == 'g':
                # wizard.save_sql()
                option = wizard.show_main_menu()
            if option_sql == 's':
                option = wizard.show_main_menu()

    return option


if __name__ == '__main__':

    echelon = EchelonAgent()
    wizard = EchelonConsole(echelon.db_cred)
    option = wizard.show_main_menu()
    option = two_steps(wizard, option)

    if option == '3':
        print(wizard.check_confs_sqls_data())
        while wizard.check_confs_sqls_data() is False:
            option = wizard.show_main_menu(wizard.string_less_data)
            option = two_steps(wizard, option)

        wizard.inside_send()
        data = {
            'echelon_db': wizard.conexion_db,
            'echelon_server_receptor': wizard.host_port,
            'echelon_sql_lector': wizard.sentence_sql,
            'echelon_lapse_seconds': wizard.lapse_time,
        }
        echelon.set_values(**data)
        wizard.save_total_conf_db()
        echelon.send_query(
            wizard.table_update,
            wizard.id_name_update,
            wizard.field_update
        )
