#! usr/bin/python3.6

import mysql.connector as mysql
from functools import wraps
import sys
import os
import inspect
from orm import Base


class Session:
    '''
    Creates a MySQLConnection object.
    conn = Session().connection OR
    with Session() as conn:
        pass
    '''

    def __init__(self, settings):
        self.settings = settings
        self.parse_settings()

        # Insert project dir to path for import of models
        self.project = os.path.dirname(inspect.getabsfile(settings))
        sys.path.insert(0, self.project)
        import models 
        self.models = Base.subclasses
        self.connection = mysql.connect(**self.CONFIG)

        try:
            self.connection.database = self.DATABASE
        except mysql.Error as e:
            if e.errno == mysql.errorcode.ER_BAD_DB_ERROR:
                self.create_database()
                self.connection.database = DATABASE
            else:
                raise e

    def parse_settings(self):
        try:
            USER = self.settings.USER
            HOST = self.settings.HOST
            DATABASE = self.settings.DATABASE
            PASSWORD = self.settings.PASSWORD
        except AttributeError as e:
            raise e

        if hasattr(self.settings, 'DEBUG'):
            self.DEBUG = self.settings.DEBUG
        else:
            self.DEBUG = False

        self.DATABASE = DATABASE

        self.CONFIG = {
                'host': HOST, 
                'user': USER, 
                'password': PASSWORD}

    def create_database(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE DATABASE %s DEFAULT CHARACTER SET 'utf8'"%DATABASE)
        cursor.close()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, trace):
        if exc_type:
            self.connection.rollback()
            self.connection.close()
            return False
        else:
            try:
                self.connection.commit()
                self.connection.close()
            except mysql.errors.InternalError:
                pass # Handle unread result in fetchone SELET queries
                        
            return True


    def commit(self):
        '''Commit the changes to the database explicitly'''
        self.connection.commit()

    def close(self):
        '''Close the mysql connection'''
        self.connection.close()

    def add(self, instance):
        '''
        Insert a record to the table 
        emp = Employee(emp_id=1, name='Jane Doe', sex='Female')
        inserted = Session().add(emp)
        Returns a bool or raises mysql.Error exception
        '''

        table = instance.__class__.__name__.lower()
        keys = ", ".join(vars(instance).keys())
        values = tuple(vars(instance).values())

        SQL = """INSERT INTO %s (%s) VALUES(""" % (table, keys)
        SQL += """ "%s",""" * len(values) % (values)
        SQL = SQL[:-1] + ")"

        if self.DEBUG: print(SQL)

        with Session(self.settings) as conn:
            try:
                c = conn.cursor()
                c.execute(SQL)
                conn.commit()
                return True
            except mysql.Error as e:
                if e.errno==1062:
                    print("Already saved to the database")
                    return True
                elif e.errno == 1146:
                    # Table does not exist
                    return True
                else:
                    raise e

                return True

    def update(self, instance):
        '''
        Update a record to the table 
        emp = Employee(emp_id=1, name='John Doe', sex='Female')
        updated = Session().add(emp)
        Returns a bool or raises mysql.Error exception
        '''

        if not self.exists(instance.__class__, instance.id):
            print("Cant update a value that does not exist")
            return False

        instance_dict = vars(instance)

        table = instance.__class__.__name__.lower()
        keys = ", ".join(instance_dict.keys())
        values = tuple(instance_dict.values())

        SQL = """UPDATE {} SET """.format(table)

        for key, value in instance_dict.items():
            SQL += """ %s = "%s" ,""" % (key, value)

        SQL = SQL[:-1] + """ WHERE id = "{}" """.format(instance.id)

        if self.DEBUG: print(SQL)

        try:
            with Session(self.settings) as conn:
                c = conn.cursor()
                c.execute(SQL)
                conn.commit()
                return True
        except Exception as e:
            raise e

    def delete(self, model_class, **where):
        '''
        Session().delete(Employee, id=1, name='John Doe')
        '''
        assert hasattr(model_class, '_fields'), 'Not a valid class'
        table = model_class.__name__.lower()

        with Session() as conn:
            SQL = f'DELETE FROM {table} WHERE'
            if not where:
                raise ValueError('Specify WHERE conditions as kwargs')

            i = 1
            for k, v in where.items():
                SQL+= " %s = '%s' "%(k,v) if i ==1 else "AND %s = '%s' "%(k,v)
                i +=1

            c= conn.cursor()
            c.execute(SQL)
            conn.commit()

    def delete_all(self, model_class):
        '''Drop all records from the table model_class.__name__.lower()
        '''
        assert hasattr(model_class, '_fields'), 'Not a valid model class'

        table = model_class.__name__.lower()
        with Session() as conn:
            SQL = f'DELETE FROM {table}'
            conn.cursor().execute(SQL)
            conn.commit()

    def typeassert(self, model_class, strict, returnDict, where):
        assert hasattr(model_class, '_fields'), 'Not a valid model class'
        assert isinstance(strict, bool), 'Expected True or False for strict'
        assert isinstance(returnDict, bool), 'Expected True or False for returnDict'

    
    def get(self, model_class, strict=True, returnDict=False, fetchOne=False, **where):
        '''params:
        model_class: The queried model class
        strict: bool -> If True, queries are run with EQUAL(=) operator.
        If False: Queries are run with RLIKE keyword
        returnDict: bool -> Return a list if dictionaries(field_names: values)
        fetchOne: bool -> cursor.fetchone() else: cursor.fetchall()
        where: **kwargs for quere WHERE condition.
        if where in {}: Returns all results in the table

        Usage:
        print(Session().get(Employee, id=1, returnDict=True))
        '''
        self.typeassert(model_class, strict, returnDict, where)

        table = model_class.__name__.lower()
        with Session(self.settings) as conn:
            if not where:
                query = f'SELECT * FROM {table}'
            else:
                query = f'SELECT * FROM {table} WHERE'
                
            index= 1
            operator = '=' if strict else 'RLIKE'

            for key, value in where.items():
                if index == 1:
                    query+= " %s %s '%s' "%(key, operator, value)
                else:
                    query+= " AND %s %s '%s' "%(key, operator, value)
                index += 1
                
            try:
                cursor=conn.cursor()
                cursor.execute(query)
            except mysql.Error as e:
                if e.errno == 1146:
                    print(f"The table {table} does not exist")
                    return []

                else:
                    raise e
            else:
                if fetchOne:
                    colnames = [d[0] for d in cursor.description]
                    results = cursor.fetchone()
                    if returnDict:
                        return {col: val for col, val in zip(colnames, results)}\
                        if results else {}
                    return results

                return self.handleResult(cursor, returnDict)


    def handleResult(self, cursor, returnDict):
        if returnDict:
            colnames = [d[0] for d in cursor.description]
            return [dict(zip(colnames, r)) for r in cursor.fetchall()]
        return cursor.fetchall()

    def description(self, model):
        table = model.__name__.lower()
        with Session(self.settings) as conn:
            c = conn.cursor()

            try:
                c.execute(f"DESCRIBE {table}")
                return [result[0] for result in c.fetchall()]
            except mysql.errors.ProgrammingError:
                # If table does not exists
                return []
                
    def execute(self, SQL, fetchOne=False):
        '''Directly execute queries
        Works on all SELECT, UPDATE, INSERT AND DELETE QUERIES
        SQL: query to execute
        fetchOne: bool >> cursor.fetchone()
        Return:
            False if an exception occurs
            True: No errors in queries
            List if select query
        '''

        with Session(self.settings) as conn:
            c = conn.cursor()
            try:
                c.execute(SQL)
            except Exception as e:
                print(str(e))
                return False
            else:
                if 'select' in str(SQL).lower():
                    results = c.fetchall()
                    return results
                return True

    def exists(self, model_class, ID):
        '''Check if a record of id==ID exists in table model_class.__name__.lower()'''

        assert hasattr(model_class, '_fields'), 'Not a valid model class'
        res = self.get(model_class, id=ID, fetchOne=True)
        if res:
            return True
        return False


    def makemigrations(self):
        ''' Do database migrations
        1. Creates new tables from models
        2. Updates columns and columns

        Returns True if no exception else raises an unhandled exception
        '''

        UNCHANGED = []

        with Session(self.settings) as conn:
            cursor = conn.cursor()
            for name, model in self.models.items():
                print("Running migrations... on table: %s"%model.__name__.lower())
                columns = self.description(model)
        
                table = name.lower()
                QUERY = "CREATE TABLE IF NOT EXISTS %s ("%table

                for field, FieldType in model.columns.items():
                    QUERY += "%s %s, " % (field, FieldType)
                    # If no columns --> Table not created yet
                    if columns:
                        self.UpdateColums(cursor, field, FieldType, 
                            model, columns, UNCHANGED)

                QUERY = QUERY[:-2] + ") ENGINE=InnoDB"
            
                print(QUERY)
                
                try:
                    cursor.execute(QUERY)
                except mysql.Error as e:
                    raise e

            return True

    def UpdateColums(self, cursor, field, FieldType, model, columns, UNCHANGED):
        '''Updates the columns. Dont call directly
        '''
        table = model.__name__.lower()
        if field not in columns:
            n = UNCHANGED.pop()
            new_sql = f"ALTER TABLE {table} ADD COLUMN {field} {FieldType} AFTER {n}"
            cursor.execute(new_sql)
            print("\n\n", new_sql)
        else:
            UNCHANGED.append(field)

        # We drop the fields in the table not in models
        TCOLS = set(columns)-set(model._fields)
        for col in TCOLS:
            columns.remove(col)
            QRY = f"ALTER TABLE {table} DROP COLUMN {col}"
            cursor.execute(QRY)
            print("\n\n", QRY)

        return True

       
__all__  = ['Session']

