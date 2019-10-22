import sqlite3, pathlib
try:
    from flaskr.utils import get_project_root
except:
    from utils import get_project_root


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    filename="ltrcol-2574-portal.db"
    project_root = get_project_root()
    file_path = project_root / "flaskr" / "data" / filename
    try:
        conn = sqlite3.connect(str(file_path))
        return conn
    except ValueError as e:
        print(e)
    return None

def create_import_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    filename="ltrcol-2574-portal.db"
    project_root = get_project_root()
    file_path = project_root / "flaskr" / "data" / "uploads" / filename
    try:
        conn = sqlite3.connect(str(file_path))
        return conn
    except ValueError as e:
        print(e)
    return None

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def create_sql_user_list(field, list_of_id):
    innerq=""
    for employee_id in list_of_id:
        innerq += field + "='{}' OR ".format(employee_id)
    return innerq.rstrip(" OR ")

def sql_fetch_all(conn, sql_query):
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        print(f"SQL String:{sql_query}")
        print(f"SQL error:{e}")
    return cursor.fetchall()

def sql_fetch_dict_all(sql_query, conn=None):

    if conn is None:
        conn = create_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        print(f"SQL String:{sql_query}")
        print(f"SQL error:{e}")
    return cursor.fetchall()

def sql_fetch_single_column_all(conn, sql_query):
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
    except sqlite3.Error as e:
        print(f"SQL String:{sql_query}")
        print(f"SQL error:{e}")
    return cursor.fetchall()

def sql_query(sql_string, db_values='', fetch_all=True):
    conn = create_connection()
    try:
        print('** before sql_query: ' + str(sql_string))
        cursor = conn.cursor()
        print('** after conn.cursor: ' + str(sql_string))
        if db_values:
            cursor.execute(sql_string,db_values)
        else:
            cursor.execute(sql_string)
            print('** after conn.execute: ' + str(sql_string))
        if 'select' in sql_string.lower():
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        conn.commit()
        print('** after conn.commit: ' + str(sql_string))
    except ValueError as e:
        print(e)

def sql_query_conn(conn, sql_string, db_values='', fetch_all=True):
    try:
        cursor = conn.cursor()
        if db_values:
            try:
                cursor.execute(sql_string,db_values)
            except sqlite3.Error as e:
                print(f"SQL String:{sql_string}")
                print(f"DB Values:{db_values}")
                print(f"SQL error:{e}")
        else:
            cursor.execute(sql_string)
        if 'select' in sql_string.lower():
            if fetch_all:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        conn.commit()
    except ValueError as e:
        print(e)
