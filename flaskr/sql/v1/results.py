from flaskr.sql.base import create_connection, dict_factory 
from flaskr.sql.base import sql_fetch_all, sql_fetch_dict_all, sql_query
from flaskr.db_tools import clean_sql_tables, build_sql_tables, RESULTS_TABLE

def results_all_results_sql(name):

    if name:
        where = f" where name = '{name}'"
    else:
        where = ''
    query = f"""
            SELECT * 
            from `results` {where}
            """
    return sql_fetch_dict_all(query)

def results_save_results_sql(data):

    count = 0

    for record in data:

        fields = []
        values = []

        for k, v in record.items():

            fields.append(k)
            values.append(str(v).replace("'", '"'))

        if fields:
            fields = ','.join(fields)
            values = "','".join(values)
            sql = f"INSERT INTO `results` ({fields}) VALUES ('{values}')"
            #print(sql)
            sql_query(sql)

        count += 1


    return {'inserted': count}

def results_update_schema_results_sql():

    clean_sql_tables('results')
    build_sql_tables(RESULTS_TABLE)
    return '1'