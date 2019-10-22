import sqlite3
import os

from flaskr.sql.base import create_connection
from flaskr.sql.base import create_import_connection
from flaskr.sql.base import sql_fetch_dict_all, sql_query_conn
from flaskr.utils import get_project_root

conn=create_connection()

UPLOADS_TABLE = """      
                        CREATE TABLE IF NOT EXISTS uploads (
                                    pkid INTEGER PRIMARY KEY,
                                    name text NOT NULL,
                                    files text
                                ); """


CMS_SPACES_TABLE = """      
                        CREATE TABLE IF NOT EXISTS cms_spaces (
                                    pkid INTEGER PRIMARY KEY,
                                    coSpaceID text,
                                    name text,
                                    passcode text,
                                    uri text,
                                    secondaryUri text
                                ); """



CALL_FLOWS_TABLE = """      
                        CREATE TABLE IF NOT EXISTS call_flows (
                                    pkid INTEGER PRIMARY KEY,
                                    name text NOT NULL,
                                    number text,
                                    department text,
                                    response text,
                                    filename text,
                                    camelot_script text,
                                    results text,
                                    test_ext text
                                ); """


RESULTS_TABLE = """      
                        CREATE TABLE IF NOT EXISTS results (
                                    pkid INTEGER PRIMARY KEY,
                                    name text NOT NULL,
                                    timestamp text,
                                    number text,
                                    status text,
                                    department text,
                                    response text,
                                    calling text,
                                    ocalled text,
                                    fcalled text,
                                    base_calling_number text,
                                    location_name text,
                                    result text,
                                    store_id text,
                                    store_phone text

                                ); """

LOCATIONS_TABLE = """      
                        CREATE TABLE IF NOT EXISTS locations (
                                    pkid INTEGER PRIMARY KEY,
                                    name text NOT NULL,
                                    store_id text,
                                    store_phone_number text,
                                    calling_number text

                                ); """

TABLES = {
    'uploads': UPLOADS_TABLE,
    'call_flows': CALL_FLOWS_TABLE,
    'cms_spaces': CMS_SPACES_TABLE,
    'results': RESULTS_TABLE,
    'locations': LOCATIONS_TABLE
}

def clean_sql_tables(table):
    sql_string = f"DROP TABLE IF EXISTS {table};"
    
    try:
        c = conn.cursor()
        c.execute(sql_string)
    except ValueError as e:
        print(e)    

def build_sql_tables(sql_string):

    try:
        c = conn.cursor()
        c.execute(sql_string)
    except ValueError as e:
        print(e)

def init_tables():

    for t, fields in TABLES.items():
        #print(t, fields)
        clean_sql_tables(t)
        build_sql_tables(fields)

def update_tables():

    for t, fields in TABLES.items():
        #print(t, fields)
        build_sql_tables(fields)

def import_db():

    import_tables = ['call_flows', 'locations', 'cms_spaces']
    db_exists = os.path.isfile(f'{str(get_project_root())}/flaskr/data/uploads/ltrcol-2574-portal.db')

    if db_exists:
        init_tables()

        import_conn = create_import_connection()

        if import_conn is None:
            return False

        for table in import_tables:

            sql = f"SELECT * FROM `{table}`"
            print(sql)
            result = sql_fetch_dict_all(sql, conn=import_conn)
            print(result)

            for record in result:

                try:
                    del record['pkid']
                except:
                    pass

                fields = []
                values = []

                for k, v in record.items():

                    fields.append(k)
                    values.append(str(v).replace("'", '"'))

                if fields:
                    fields = ','.join(fields)
                    values = "','".join(values)
                    sql = f"INSERT INTO `{table}` ({fields}) VALUES ('{values}')"
                    print(sql)
                    sql_query_conn(conn, sql)

        return True
    
    return False

