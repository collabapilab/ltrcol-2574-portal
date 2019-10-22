import json
import os

from flaskr.sql.base import create_connection, dict_factory 
from flaskr.sql.base import sql_fetch_all, sql_fetch_dict_all, sql_query
from flaskr.utils import get_project_root

def upload_alluploads_sql():
    conn = create_connection()
    query = f"""
            SELECT * 
            from `uploads`
            """


    return sql_fetch_dict_all(query)

def upload_clear_uploads(name):

    query = f"""
            UPDATE `uploads` SET files = ""
            where name = '{name}'
            """

    return sql_query(query)

def list_files(name):


    path = f'{str(get_project_root())}/flaskr/data/uploads/traces/{name}/'

    filenames = []
    for root,d_names,f_names in os.walk(path):

        for filename in f_names:

            if filename[-4:] == '.txt' or filename[-3:] == '.gz':
                filenames.append(os.path.join(root, filename))

    return filenames

def upload_update_uploads(name):

    filenames = list_files(name)
    root_path = f'{str(get_project_root())}/flaskr/data/uploads/traces/'
    filenames = ','.join(sorted([x.replace(root_path, '') for x in filenames]))

    query = f"""
            UPDATE `uploads` SET files = "{str(filenames)}"
            where name = '{name}'
            """

    return sql_query(query)

def upload_all_tests_sql():
    conn = create_connection()
    query = f"""
            SELECT DISTINCT name
            from `uploads`
            """


    result = sql_fetch_all(conn, query)

    return [x[0] for x in result]

def upload_all_files_sql(name):

    conn = create_connection()
    query = f"""
            SELECT files 
            FROM `uploads`
            WHERE name = '{name}'

    """
    print('** all files', name)
    result = sql_fetch_dict_all(query)

    if result:

        result = result[0]['files']

        result = result.split(',')
    
    return result


def upload_all_files_details_sql():

    conn = create_connection()
    query = f"""
            SELECT * 
            FROM `files`
            
    """

    result = sql_fetch_dict_all(query)

    details = {}

    for detail in result:

        details[detail['filename']] = detail

    return details

def upload_wav_files_sql():



    result = upload_alluploads_sql()

    tests = result['data']
    files = result['files']['files']

    wav_files = []

    for test in tests:

        test_files = test['files']

        for t in test_files:
            print(type(t['id']))
            wav_files.append({
                'name': test['name'],
                'filename': files[int(t['id'])]['filename']
            })

    return wav_files




def customer_resolved_sql(id, years):
    conn = create_connection()
    query = f"""
            SELECT * 
            from `defects` as d
            inner join `customer_defects` as c  on c.id = d.id
            WHERE ( Customer_id = '{id}' AND 
                    ({sql_status_gen("resolved")}) AND
                    ( Submitted_date >= date('now','-{years} year') ) 
                   )
            """
    return sql_fetch_dict_all(query)

def customer_closed_sql(id, years):
    conn = create_connection()
    query = f"""
            SELECT * 
            from `defects` as d
            inner join `customer_defects` as c  on c.id = d.id
            WHERE ( Customer_id = '{id}' AND 
            ({sql_status_gen("closed")}) AND
            ( Submitted_date >= date('now','-{years} year') )  
            )"""
    return sql_fetch_dict_all(conn, query)

def customer_active_sql(id, years):
    conn = create_connection()
    query = f"""
            SELECT * 
            from `defects` as d
            inner join `customer_defects` as c  on c.id = d.id
            WHERE ( Customer_id = '{id}' and 
                  ({sql_status_gen("active")}) AND
                  ( Submitted_date >= date('now','-{years} year') )  
                  )
            """
    return sql_fetch_dict_all(conn, query)

def customer_state_sql(id, state, years):
    conn = create_connection()
    query = f"""
            SELECT *
            from `defects` as d
            inner join `customer_defects` as c  on c.id = d.id
            WHERE ( Customer_id = '{id}' and 
                  ( Status = '{state}' ') AND
                  ( Submitted_date >= date('now','-{years} year') )  
                  )
            """
    return sql_fetch_dict_all(conn, query)


def customer_statecount_sql(id, years):
    conn = create_connection()
    query = f"""
            SELECT Status,COUNT(Status)
            from `defects` as d
            inner join `customer_defects` as c  on c.id = d.id
            WHERE Customer_id = "{id}" AND 
            ( Submitted_date >= date('now','-{years} year') ) 
            GROUP BY Status
            ORDER BY Status DESC"""
    return sql_fetch_all(conn, query)

def customer_submit_by_month_sql( id, years):
    conn = create_connection()
    query = f"""
        SELECT strftime('%Y-%m',Submitted_date) as Month,COUNT(d.id) as Total 
        from `defects` as d
        inner join `customer_defects` as c  on c.id = d.id
        WHERE Submitted_date >= date('now','-{years} year') AND 
        ( Customer_id = '{id}')
        GROUP BY strftime('%Y-%m',Submitted_date)
        ORDER BY Submitted_date ASC
        """
    return sql_fetch_all(conn, query)



def customer_srcountmonth_sql(id, years):
    conn = create_connection()
    query = f"""
        SELECT strftime('%Y-%m',Submitted_date) as Month,SUM(Ticket_count)
        from `defects` as d
        inner join `customer_defects` as c  on c.id = d.id
        WHERE Submitted_date >= date('now','-{int(years)} year') AND (Customer_id = '{id}')
        GROUP BY strftime('%Y-%m',Submitted_date)
        ORDER by Submitted_date ASC
        """
    return sql_fetch_all(conn, query)

def customer_product_count_sql(id, year,limit):
    conn = create_connection()
    query = f"""
        SELECT Product,COUNT(d.id) as Total
        from `defects` as d
        inner join `customer_defects` as c  on c.id = d.id
        WHERE Submitted_date >= date('now','-{int(year)} year') AND (Customer_id='{id}')
        GROUP BY Product
        ORDER BY Total DESC
        {"" if limit == 0 else "LIMIT "+limit }
        """
    return sql_fetch_all(conn, query)

def customer_component_count_sql(id, year,limit):
    conn = create_connection()
    query = f"""
        SELECT Component,COUNT(d.id) as Total 
        from `defects` as d
        inner join `customer_defects` as c  on c.id = d.id
        WHERE Submitted_date >= date('now','-{int(year)} year') AND (Customer_id='{id}')
        GROUP BY Component 
        ORDER BY Total DESC
        {"" if limit == 0 else "LIMIT "+limit }
        """
    return sql_fetch_all(conn, query)

def getAll_sql():
    conn = create_connection()
    cur = conn.cursor()
    query = """
        SELECT distinct Customer_id from customer_defects
        """
    cur.execute(query)
    return cur.fetchall()

