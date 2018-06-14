# -*- coding: utf-8 -*-
"""
    zebe.util.sqlite_util
    ~~~~~~~~~~~~~~~~

    sqlite工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import sqlite3


def get_connection(db_file_path):
    """
    获取连接
    :param db_file_path: 数据库文件路径
    :return: 返回数据库连接
    """
    return sqlite3.connect(db_file_path, check_same_thread=False)


def execute_sql(connection, sql):
    """
    执行SQL语句
    :param connection: 数据库连接
    :param sql: SQL语句
    :return:
    """
    if connection is not None and len(sql) > 0:
        connection.cursor().execute(sql)
        connection.commit()


def find_all(connection, sql):
    """
    查询全部
    :param connection: 数据库连接
    :param sql: SQL语句
    :return: 返回查询的数据元祖
    """
    if connection is not None and len(sql) > 0:
        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    else:
        return []