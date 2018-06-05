import psycopg2, psycopg2.extras, json
from datetime import datetime
from psycopg2.extensions import AsIs

class Psyshort():
    def __init__(self, hostname, dbname, username, password):
        self.hostname = hostname
        self.dbname = dbname
        self.username = username
        self.password = password
        self.connect_datetime = self.connect()
        
    def __del__(self):
        self.disconnect()
    
    def connect(self):
        self.conn = psycopg2.connect(
            """dbname='{dbname}'
            user='{user}'
            host='{host}'
            password='{password}'""".format(
                dbname=self.dbname,
                user=self.username,
                host=self.hostname,
                password=self.password
                )
            )
        return datetime.now()
        
    def disconnect(self):
        self.conn.close()
        return (datetime.now() - self.connect_datetime)
        
    def select(self, table, fields=None, where=None, limit=None, order_by=None):
        select_start = datetime.now()
        records = []
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            query = "SELECT"
            if fields:
                query += " ("
                for field in fields:
                    query += "{0}, ".format(field)
                    
                query += ")"
            
            else:
                query += " *"
            
            query += " FROM {table}".format(table=table)
            if where:
                query += " WHERE {0}".format(where)
                
            if limit:
                query += " LIMIT {0}".format(limit)
                
            if order_by:
                query += " ORDER BY {0}".format(order_by)
                
            try:
                cur.execute(query)
                
            except psycopg2.IntegrityError as eX:
                self.conn.rollback()
                return False
                
            else:
                for row in cur.fetchall():
                    records.append(dict(row))
                    
        return {
            "result": records,
            "duration": (datetime.now() - select_start)
            }
        
    def insert(self, table, columns, row):
        with self.conn.cursor() as cur:
            values = [
                row[column] for column in columns
                ]
            query = "INSERT INTO {table} (%s) VALUES %s".format(table=table)
            try:
                cur.execute(
                    cur.mogrify(
                        query,
                        (
                            AsIs(
                                ','.join(columns)
                                ),
                            tuple(values)
                            )
                        )
                    )
                
            except psycopg2.IntegrityError as eX:
                self.conn.rollback()
                return False
                
            self.conn.commit()
            return True
        
    def insert_multi(self, table, columns, rows):
        insert_start = datetime.now()
        failed_rows = []
        with self.conn.cursor() as cur:
            headers = ", ".join(columns)
            values = [
                tuple(
                    [
                        row[column] for column in columns
                        ]
                    )
                for row in rows
                ]
            query = "INSERT INTO {table} ({headers}) VALUES %s".format(
                table=table,
                headers=headers
                )
            try:
                psycopg2.extras.execute_values(
                    cur=cur,
                    sql=query,
                    argslist=values
                    )
                
            except psycopg2.IntegrityError as eX:
                self.conn.rollback()
                for row in rows:
                    if not self.insert(table, columns, row):
                        failed_rows.append(row)
                        
            self.conn.commit()
            return {
                "failed_rows": failed_rows,
                "duration": (datetime.now() - insert_start),
                }