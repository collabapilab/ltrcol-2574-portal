import logging
from dotenv import load_dotenv
from os.path import abspath, join, dirname
from sys import exit

log = logging.getLogger(__name__)

# Load environment variables from .env
env_file = abspath(join(dirname(__file__), '..', '.env'))
log.info(f'Reading {env_file}')
if not load_dotenv(env_file):
    exit(f'ERROR: Cannot load environment file: {env_file}')


from flask import Flask
from flask_cors import CORS
from flaskr.routes import core
from flaskr.api.v1 import v1_blueprint

app = Flask(__name__, static_folder=None)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.register_blueprint(core, url_prefix='/')
app.register_blueprint(v1_blueprint, url_prefix='/api/v1')


# This is required to avoid net::ERR_INVALID_HTTP_RESPONSE (304) when client
# requests the static/js resources from the flask app
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store'
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True)
