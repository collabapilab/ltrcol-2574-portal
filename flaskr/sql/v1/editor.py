import re

from flaskr.sql.base import create_connection, dict_factory 
from flaskr.sql.base import sql_query
from flaskr.sql.base import sql_fetch_all, sql_fetch_dict_all


def parse_DT_request(form):

    #
    print('get_request_data form:', form)
    data = {}

    for record in form:
        #
        print('record', record)

        value = form[record]

        match = re.findall(r'\[([A-Za-z0-9_\-]+)\]', record)

        if match:
            #print('match', match, value)
            pkid = int(match.pop(0))

            if pkid not in data:
                data[pkid] = {}

            key = match.pop(0)

            print('remaining', match)

            if key == 'pkid' and (pkid == 0 or value == ''):
                continue

            # multiple values contained in a list, ie files-many-count
            if len(match) > 0:

                if key not in data[pkid]:
                    data[pkid][key] = []
                data[pkid][key].append({match[-1]: value})

            # Don't keep and keys with files-many-count or *-many-count
            elif 'many-count' in key:
                if str(value) == '0':
                    field = key.split('-')[0]
                    data[pkid][field] = ''
            else:
                data[pkid][key] = value

    print('returning data', data)
    return data

def editor_create(table, data):

    #record = data.get(0, {})

    return_limit = len(data.keys())
    for key in data:

        record = data[key]
        print('*** record', record)
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
            sql_query(sql)

    sql = f'SELECT * FROM `{table}` ORDER BY PKID LIMIT {str(return_limit)}'
    print(sql)
    result = sql_fetch_dict_all(sql)
    print(result)

    return {'data': result}



def editor_edit(table, data):
    #print('editing', data)
    for pkid in data:
        #print('pkid', pkid)
        record = data[pkid]

        try:
            del record['pkid']
        except:
            pass

        #print(record)

        fields = []

        for k, v in record.items():

            v = str(v).replace("'", '"')
            fields.append(f"{k}='{v}'")

        if fields:
            fields = ','.join(fields)
            sql = f"UPDATE `{table}` SET {fields} where pkid='{pkid}'"
            print(sql)
            sql_query(sql)

    pkids = "','".join([str(x) for x in data.keys()])
    sql = f"SELECT * FROM `{table}` where pkid in ('{pkids}')"
    #print(sql)
    result = sql_fetch_dict_all(sql)
    #print(result)

    return {'data': result}
        

def editor_remove(table, data):

    pkids = []
    print('editor_remove data: ' + str(data))
    for pkid in data.keys():
        print(pkid)
        pkids.append(f"pkid='{pkid}'")

    pkids = ' or '.join(pkids)
    sql = f"DELETE FROM `{table}` where {pkids}"
    #print(sql)
    sql_query(sql)

    pkids = "','".join([str(x) for x in data.keys()])
    sql = f"SELECT * FROM `{table}` where pkid in ('{pkids}')"
    #print(sql)
    result = sql_fetch_dict_all(sql)
    #print(result)

    return result
        

