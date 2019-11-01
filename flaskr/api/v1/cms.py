from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields
from flaskr.cms.v1.cms import *
import xmltodict
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
        base_url = '/api/v1/system/status'
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url)

        return result


@api.route("/version")
class cms_version_api(Resource):
    # @api.expect(system_status_data)
    def get(self,host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves the version of the CMS system software.

        Use this method to query for the CMS software version.
        """
        base_url = '/api/v1/system/status'
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url)
        if result['success']:
            return jsonify({'success': True, 'version': result['response']['status']['softwareVersion']})
        else:
            return jsonify(result)


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
# @api.response(404, 'CMS Space not found.')
class cms_create_space_api(Resource):

    @api.expect(create_space_data)
    def post(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Creates a new CMS Space.

        Use this method to add a new Space.

        * Send a JSON object with optional parameters, such as name, uri, secondaryUri, passcode, defaultLayout, etc in the request body.

        ```
        {
          "name": "Name of the Space",
          "uri": "User URI part for SIP call to reach Space",
          "secondaryUri": "Secondary URI for SIP call to reach Space",
          "passcode": "The security code for this Space",
          "defaultLayout": "The default layout to be used for new call legs in this Space.  May be:  allEqual | speakerOnly | telepresence | stacked"
        }
        ```

        * Returns a dictionary with a 'success' (boolean) element.  If success is true, then the ID of the new Space is returned in the 'id' key.  Otherwise, a 'message element will contain error information.
        """
        # json_data = self.api.payload

        base_url = '/api/v1/coSpaces'
        # if self.api.payload:
        #     payload = urllib.parse.urlencode(self.api.payload)
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url, body=self.api.payload, request_method='POST')

        return jsonify(result)

        # new_space = cms_send_request(host=host, username=username, password=password, port=port, location=base_url, body=payload, request_method='POST')
        # if new_space:
        #     if new_space.status_code == 200:
        #         return jsonify({'success': True, 'id': new_space.headers._store['location'][1][len("/api/v1/coSpaces/"):]})
        #     else:
        #         failure_msg = json.loads(json.dumps(xmltodict.parse(new_space.content)))
        #         return jsonify({'success': False, 'message': failure_msg})
        # else:
        #     return jsonify({'success': False, 'message': new_space.reason})


@api.route("/edit_space/<id>")
class cms_edit_api(Resource):
    def put(self, id, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Edits a CMS space
        """
        base_url = '/api/v1/coSpaces/' + id
        # if self.api.payload:
        #     payload = urllib.parse.urlencode(self.api.payload)
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url, body=self.api.payload, request_method='PUT')

        return result


@api.route("/spaces", "/coSpaces", "list_spaces")
class cms_get_spaces_api(Resource):
    def get(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves CMS Spaces.

        Use this method to retrieve a list of Spaces.

        """

        base_url = '/api/v1/coSpaces'
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url)

        return result


@api.route("/space/<id>")
class cms_get_space_api(Resource):
    def get(self, id, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Retrieves CMS Spaces.

        Use this method to retrieve a list of Spaces.

        """

        base_url = '/api/v1/coSpaces/' + str(id)
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url)

        return result


@api.route("/delete_space/<id>")
class cms_remove_space_api(Resource):
    def delete(self, id, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
        """
        Removes a CMS space
        """
        base_url = '/api/v1/coSpaces/' + str(id)
        result = cms_send_request(host=host, username=username, password=password, port=port, location=base_url, request_method='DELETE')
        return result


