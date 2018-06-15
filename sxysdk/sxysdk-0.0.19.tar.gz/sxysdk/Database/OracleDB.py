# -*- coding:utf-8 -*-
import cx_Oracle

import logging
logger = logging.getLogger('sxysdk.OracleDB')

class OracleDB:
    """提供Oracle数据库的基本操作
    参数：
        host:Oracle主机名（IP或计算机名）
        db_user_name:数据库用户名
        db_passwd:数据库密码
        service_name:数据库服务名
        port:端口号，默认1521
        protocol:连接协议，默认TCP
    方法：
        Query:查询
        Exec:增、删、改
    """

    def __init__(self, host, db_user_name, db_passwd, service_name, port=1521, protocol='TCP'):
        self._host = host
        self._db_user_name = db_user_name
        self._db_passwd = db_passwd
        self._service_name = service_name
        self._port = port
        self._protocol = protocol
        self._conn = None
        self.ReConnect()

    def ReConnect(self):
        if not self._conn:
            tns = '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL={})(HOST={})' \
                  '(PORT={})))(CONNECT_DATA=(SERVICE_NAME={})))'.format(self._protocol,
                                                                        self._host,
                                                                        self._port,
                                                                        self._service_name)
            try:
                self._conn = cx_Oracle.connect(self._db_user_name, self._db_passwd, tns)
            except cx_Oracle.DatabaseError:
                self._conn = cx_Oracle.connect(self._db_user_name, self._db_passwd, tns, cx_Oracle.SYSDBA)
        else:
            pass

    def __del__(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def NewCursor(self):
        cur = self._conn.cursor()
        if cur:
            return cur
        else:
            logging.debug("#Error# Get New Cursor Failed.")
            return None

    def DelCursor(self, cur):
        if cur:
            cur.close()

    def Commit(self):
        if self._conn:
            self._conn.commit()

    def Execute(self, cur, sql):
        rt = True
        rs = None
        if cur:
            try:
                cur.execute(sql)
            except cx_Oracle.DatabaseError as e:
                rs = str(e)
                rt = False
        return rt, rs

    # 检查sql语句
    def PermitedUpdateSql(self, sql):
        rt = True
        lrsql = sql.lower()
        sql_elems = lrsql.strip().split()

        # 更新删除语句，判断首单词，不带where语句的sql不予执行
        if sql_elems[0] in ['update', 'delete']:
            if 'where' not in sql_elems:
                rt = False

        return rt

    # 导出结果为文件
    def Export(self, sql, file_name, colfg = '||'):
        rt = self.Query(sql)
        if rt:
            with open(file_name, 'a') as fd:
                for row in rt:
                    ln_info = ''
                    for col in row:
                        ln_info += str(col) + colfg
                    ln_info += '\n'
                    fd.write(ln_info)
                    fd.close()

    # 查询
    def Query(self, sql, nStart=0, nNum=-1):
        rt = None
        rs = []

        # 获取cursor
        cur = self.NewCursor()
        if not cur:
            return rt,rs

        rt, rs = self.Execute(cur, sql)
        if rt:
            rs = []  # 查询结果放入列表
            if (nStart == 0) and (nNum == 1):
                rs.append(cur.fetchone())
            else:
                rs = cur.fetchall()
                if nNum == -1:
                    rs.extend(rs[nStart:])
                else:
                    rs.extend(rs[nStart:nStart + nNum])

        # 释放cursor
        self.DelCursor(cur)

        return rt, rs

    # 增、删、改
    def Exec(self, sql):
        # 获取cursor
        rt = None
        rs = None
        cur = self.NewCursor()
        if not cur:
            return rt, rs

        # 判断sql是否允许其执行
        if not self.PermitedUpdateSql(sql):
            return rt, rs

        # 执行语句
        rt, rs = self.Execute(cur, sql)

        # 释放cursor
        self.DelCursor(cur)

        # commit
        self.Commit()

        return rt, rs