from flask import Flask, jsonify
from flask_cors import CORS
from flaskr.routes import core
from flaskr.api.v1 import v1_blueprint

app = Flask(__name__)
app.secret_key = 'my unobvious secret key'  #workaround for Flask flash()
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.register_blueprint(core, url_prefix='/')
app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True)
