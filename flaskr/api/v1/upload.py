import shutil

from flask import jsonify, request
from flaskr.sql.base import sql_query
from flask import Blueprint
from flaskr.sql.v1.upload import *
from flaskr.sql.v1.editor import *
from flask_restplus import Namespace, Resource

from flaskr.utils import get_project_root

api = Namespace('upload', description='File Upload APIs')

def save_uploaded_file(upload):

    # filename and file contents
    filename = upload.filename
    #print(type(upload))
    #print(dir(upload))
    #print(dir(upload.stream))
    #upload_file = upload.getvalue()

    # Store flaskr/data/uploads
    project_root = get_project_root()
    file_path = str(project_root / "flaskr" / "data" / "uploads" / filename)
    #file_path = str(project_root / "flaskr" / "data" / "uploads")
    try:
        #with open(file_path, 'wb') as f:
        #    f.write(upload_file)
        upload.save(file_path)
    except Exception as e:
        print('error:', e)
    else:
        result = {'filename': filename,
                    'filesize': upload.content_length,
                    'web_path': file_path,
                    'timestamp': "STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW','localtime')"
                    }

        sql = f"INSERT OR IGNORE INTO `files` (filename) VALUES ('{filename}')"
        sql_query(sql)

        fields = []
        for k, v in result.items():
            if k == 'timestamp':
                fields.append(f"{k}={v}")
            else:
                fields.append(f"{k}='{v}'")

        fields = ','.join(fields)

        sql = f"UPDATE `files` SET {fields} where filename='{filename}'"
        sql_query(sql)

        sql = f"SELECT * FROM `files` WHERE filename='{filename}'"

        result = sql_fetch_dict_all(sql)

        if result:
            return result

    return {}



@api.route("/upload")
class upload_file_create_api(Resource):
    def post(self):
        """
        Returns Editor Create
        """
        #print(dir(request))
        #print(request.values)
        #print(request.form)

        # Get uploaded file
        upload = request.files['upload']

        result = save_uploaded_file(upload)

        """
        {
            "files": {
                "files": {
                    "1": {
                        "filename": "Screen Shot.png",
                        "web_path": "\/upload\/1.png"
                    }
                }
            },
            "upload": {
                "id": "1"
            }
        }

        [
            {'id': 1, 
            'filename': 'SEP007970030401_4792730060_tmpfile8uB9ME.rtp.g711.wav', 
            'timestamp': '2019-10-03 18:55:42.136', 
            'filesize': '333804', 
            'web_path': '/usr/src/app/flaskr/data/uploads/SEP007970030401_4792730060_tmpfile8uB9ME.rtp.g711.wav'}
        ]
        """

        files = {
            'files': {},
            'upload': {}
        }
        if result:
            result = result[0]
            id = result['id']
            files['files'] = { 'files': { f'{id}': {
                            'filename': result['filename'],
                            'web_path': result['web_path']
                        }}
                        
            }

            files['upload'] = {
                'id': str(id)
            }

        print('files', files)
        return jsonify(files)

@api.route("/create")
class upload_create_api(Resource):
    def post(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_create('uploads', data))

@api.route("/edit")
class upload_edit_api(Resource):
    def put(self, **kwargs):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print('preedit data', data)

        result = editor_edit('uploads', data)

        for r in result['data']:
            try:
                r['files'] = json.loads(r['files'])
            except:
                r['files'] = []

        return jsonify(result)

@api.route("/remove")
class upload_delete_api(Resource):
    def post(self, **kwargs):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)

        for k, row in data.items():
            name = row['name']

            shutil.rmtree(f'{str(get_project_root())}/flaskr/data/uploads/traces/{name}/', ignore_errors=True)
        return jsonify(editor_remove('uploads', data))




@api.route("/alluploads")
class upload_api(Resource):
    def get(self):
        """
        Returns Uploaded files.
        """
        return jsonify(upload_alluploads_sql())

@api.route("/all_tests")
class upload_all_tests_api(Resource):
    def get(self):
        """
        Returns unique list of test names.
        """
        return jsonify(upload_all_tests_sql())

@api.route("/all_files_details")
class upload_all_files_details_api(Resource):
    def get(self):
        """
        Returns unique list of test names.
        """
        return jsonify(upload_all_files_details_sql())

@api.route("/<name>/all_files")
class upload_all_files_api(Resource):
    def get(self, name):
        """
        Returns Uploaded filenames for test.
        """
        return jsonify(upload_all_files_sql(name))

@api.route("/wav_files")
class upload_wav_files_api(Resource):
    def get(self):
        """
        Returns unique list of test names.
        """
        return jsonify(upload_wav_files_sql())

@api.route('/rmdir/<filepath>')
class upload_rmdir(Resource):
    def get(self, filepath):

        shutil.rmtree(f'{str(get_project_root())}/flaskr/data/uploads/traces/{filepath}/', ignore_errors=True)

        return jsonify(upload_clear_uploads(filepath))

@api.route('/update_files/<name>')
class upload_update(Resource):
    def get(self, name):


        return jsonify(upload_update_uploads(name))

    