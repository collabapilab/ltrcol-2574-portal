
from flask import jsonify, request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields
from flaskr.cms.v1.cms import *

api = Namespace('cms', description='Cisco Meeting Server REST API')

system_status_data = api.model('CMS System Status', {
    'host': fields.String(description='CMS host/IP', default=default_cms['host'], required=False),
    'port': fields.Integer(description='port', default=default_cms['port'], required=False),
    'username': fields.String(description='CMS API user name', default=default_cms['username'], required=False),
    'password': fields.String(description='CMS API user password', default='********', required=False),
})

@api.route("/system_status")
class cms_system_status_api(Resource):
    # @api.expect(system_status_data)
    def get(self,host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves the CMS system status.

        Use this method to query for the CMS system status.
        """
        status = get_system_status_api(ip=host, username=username, password=password, port=str(port))

        return jsonify(status)


@api.route("/version")
class cms_version_api(Resource):
    # @api.expect(system_status_data)
    def get(self,host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves the version of the CMS system software.

        Use this method to query for the CMS software version.
        """
        status = get_system_status_api(ip=host, username=username, password=password, port=str(port))

        if status:
            return jsonify(status['status']['softwareVersion'])
        else:
            return jsonify(status)


def lookup_value(data, dict_var):
    try:
        return data[dict_var]
    except:
        return None


create_space_data = api.model('cms_space', {
    'host': fields.String(description='CMS host/IP', default=default_cms['host'], required=False),
    'port': fields.Integer(description='port', default=default_cms['port'], required=False),
    'username': fields.String(description='CMS API user name', default=default_cms['username'], required=False),
    'password': fields.String(description='CMS API user password', default='********', required=False),
    'name': fields.String(description='Name of the Space', default='', required=False),
    'uri': fields.String(description='User URI part for SIP call to reach Space', default='', required=False),
    'secondaryUri': fields.String(description='Secondary URI for SIP call to reach Space', default='', required=False),
    'passcode': fields.String(description='The security code for this Space', default='', required=False),
    'defaultLayout': fields.String(description='The default layout to be used for new call legs in this Space.  May be allEqual | speakerOnly | telepresence | stacked', default='', required=False)
} )
@api.route("/create_space")
@api.response(404, 'CMS Space not found.')
class cms_create_space_api(Resource):

    @api.expect(create_space_data)
    def post(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password'], name=None, uri=None, secondaryUri=None, passcode=None, defaultLayout=None):
        """
        Creates a new CMS Space.

        Use this method to add a new Space.

        * Send a JSON object with optional parameters, such as name, uri, secondaryUri, passcode, and defaultLayout in the request body.

        ```
        {
          "name": "My New Space"
          "uri": "User portion of the uri"
        }
        ```

        * Specify the ID of the category to modify in the request URL path.
        """
        json_data = request.json
        host = lookup_value(json_data, 'host') or host
        port = lookup_value(json_data, 'port') or port
        username = lookup_value(json_data, 'username') or username
        password = lookup_value(json_data, 'password') or password
        name = lookup_value(json_data, 'name')
        uri = lookup_value(json_data, 'uri')
        secondaryUri = lookup_value(json_data, 'secondaryUri')
        passcode = lookup_value(json_data, 'passcode')
        defaultLayout = lookup_value(json_data, 'defaultLayout')
        
        new_space = create_space_api(ip=host, port=str(port), username=username, password=password, name=name, uri=uri, secondaryUri=secondaryUri, passcode=passcode, defaultLayout=defaultLayout)
        if new_space.status_code == 200:
            return jsonify(new_space.headers._store['location'][1])
        else:
            return new_space.text or new_space.reason

@api.route("/get_spaces")
class cms_get_spaces_api(Resource):
    def get(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves CMS Spaces.

        Use this method to retrieve a list of Spaces.

        """
        return jsonify(get_spaces_api(ip=host, port=str(port), username=username, password=password))


@api.route("/remove_space")
class cms_remove_space_api(Resource):
    def post(self):

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_remove('cms_spaces', data))

@api.route("/edit_space")
class cms_edit_api(Resource):
    def put(self):
        """
        Returns Editor Create
        """

        print('request:\n', request.form)
        data = parse_DT_request(request.form)

        print(data)
        return jsonify(editor_edit('cms_spaces', data))

