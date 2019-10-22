from flaskr.sql.base import create_connection, dict_factory 
from flaskr.sql.base import sql_fetch_all, sql_fetch_dict_all

def cms_all_cms_sql():
    query = f"""
            SELECT * 
            from `cms_spaces`
            """
    return sql_fetch_dict_all(query)



def cms_get_cms_sql(name):
    query = f"""
            SELECT * 
            from `cms_spaces`
            where name='{name}'
            """
    result = sql_fetch_dict_all(query)
    dict_result = {}

    for r in result:

        cf_number = f"0{r['number'].replace('#', '0')}"[-2:]

        dict_result[cf_number] = r
    
    return dict_result

def cms_cms_names_sql():
    conn = create_connection()
    query = f"""
            SELECT distinct name 
            from `cms_spaces`
            """
    result = sql_fetch_all(conn, query)
    return [x[0] for x in result]



def cms_get_spaces_sql():
    query = f"""
            SELECT * 
            from `cms_spaces`
            """
    return sql_fetch_dict_all(query)
