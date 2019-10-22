import os
import pathlib

from flask import render_template
from flask import Blueprint
from flask import request
from flask import send_file
from flask import flash
from flask import redirect
from flask import send_from_directory
from flaskr.core_func import create_footer_urls
from flaskr.utils import get_project_root
from werkzeug.utils import secure_filename
from flaskr.db_tools import init_tables, import_db

core = Blueprint('', __name__,
                template_folder='templates',
                static_folder='static')

@core.route('/')
def index():
    print("App root is:"+ get_project_root().as_uri() )
    return render_template('main.html',
                           title='LTRCOL-2574 Collaboration APIs',
                           footer_urls=create_footer_urls())

# https://www.roytuts.com/python-flask-file-upload-example/
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = set(['db',])

@core.route('/music/<path:filename>')
def download_file(filename):
    return send_from_directory(f'{str(get_project_root())}/flaskr/data/uploads/', filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_filepath(filepath):

    path_list = filepath.split('/')

    if len(path_list) == 0 or len(path_list) == 1:
        return ''
    if len(path_list) == 2:
        return path_list[0]
    
    return f'{path_list[0]}/{path_list[1]}'


def make_directory(filepath):
    pathlib.Path(f'{str(get_project_root())}/flaskr/data/uploads/{filepath}/').mkdir(parents=True, exist_ok=True) 

def update_file_list(name, filename):
    print('** update_file_list', filename)
    upload_update_uploads(name, filename)


@core.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        filepath = request.form.get('fullPath', '')
        #filepath = parse_filepath(request.form.get('fullPath', ''))
        test_name = request.form.get('test_name', 'unknown')


        if test_name:
            filepath = f'traces/{test_name}/{filepath}'
        else:
            filepath = f'traces/{filepath}'

        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file:
            make_directory(filepath)
            filename = secure_filename(file.filename)
            file.save(os.path.join(f'{str(get_project_root())}/flaskr/data/uploads/{filepath}/', filename))
            flash('File successfully uploaded')

            return redirect('/')
        else:
            #flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            flash('Allowed to only upload ivr_sqlite.db')
            return redirect(request.url)

"""
Database tools
"""
@core.route('/getDB') 
def get_db():
    return send_file(f'{str(get_project_root())}/flaskr/data/ivr_sqlite.db',
                     mimetype='application/octet-stream',
                     attachment_filename='ivr_sqlite.db',
                     as_attachment=True)

@core.route('/emptyDB') 
def empty_db():
    init_tables()
    flash('empty ivr_sqlite.db complete')
    return redirect('/')

@core.route('/importDB') 
def import_database():
    result = import_db()
    if result:
        flash('import ivr_sqlite.db complete')
    else:
        flash('import ivr_sqlite.db FAILED')
    return redirect('/')


@core.route('/upload')
def upload_route():
    return render_template('upload.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/files')
def files_route():
    return render_template('files.html',
                            title='LTRCOL-2574 Sample Portal')

"""
Configuration pages
"""
@core.route('/call_flows')
def call_flows_route():
    return render_template('call_flows.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/locations')
def locations_route():
    return render_template('locations.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/keywords')
def keywords_route():
    return render_template('keywords.html',
                            title='LTRCOL-2574 Sample Portal')

"""
Processing and reports pages
"""
@core.route('/wav_to_text')
def kwav_to_text_route():
    return render_template('wav_to_text.html',
                            title='LTRCOL-2574 Sample Portal')
@core.route('/process')
def process_route():
    return render_template('process.html',
                            title='LTRCOL-2574 Sample Portal')
@core.route('/reports')
def reports_route():
    return render_template('reports.html',
                            title='LTRCOL-2574 Sample Portal')

"""
@core.route('/customer')
def customer_route():
    id = request.args.get('id', '')
    return render_template('customer.html',
                            title='DRIP-NG',
                            id=id)
"""

@core.route('/cucm')
def cucm_route():
    return render_template('cucm.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/cuc')
def cuc_route():
    return render_template('cuc.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/cms')
def cms_route():
    return render_template('cms.html',
                            title='LTRCOL-2574 Sample Portal')

@core.route('/teams')
def teams_route():
    return render_template('teams.html',
                            title='LTRCOL-2574 Sample Portal')



