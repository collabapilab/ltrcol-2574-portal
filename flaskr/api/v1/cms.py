from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, reqparse, fields
from flaskr.cms.v1.cms import CMS

api = Namespace('cms', description='Cisco Meeting Server REST API')

default_cms = {
    'host': 'cms1a.pod31.col.lab',
    'port': 8443,
    'username': 'admin',
    'password': 'c1sco123'
}


@api.route("/system_status")
class cms_system_status_api(Resource):
    def get(self):
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.get_system_status()


@api.route("/version")
class cms_version_api(Resource):
    # @api.expect(system_status_data)
    def get(self):
        """
        Retrieves the version of the CMS system software.

        Use this method to query for the CMS software version.
        """
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        cms_status = cms.get_system_status()
        if cms_status['success']:
            return cms_status['message']['status']['softwareVersion']
        return cms_status


create_space_data = api.model('cms_space', {
    'host': fields.String(description='CMS host/IP', default=default_cms['host'], required=False),
    'port': fields.Integer(description='port', default=default_cms['port'], required=False),
    'username': fields.String(description='CMS API user name', default=default_cms['username'], required=False),
    'password': fields.String(description='CMS API user password', default='********', required=False),
    'name': fields.String(description='Name of the Space', default='', required=False),
    'uri': fields.String(description='User URI part for SIP call to reach Space', default='', required=False),
    'secondaryUri': fields.String(description='Secondary URI for SIP call to reach Space', default='', required=False),
    'passcode': fields.String(description='The security code for this Space', default='', required=False),
    'defaultLayout': fields.String(description='The default layout to be used for new call legs in this Space. ' +
                                               'May be allEqual | speakerOnly | telepresence | stacked',
                                               default='', required=False)
})

space_args = reqparse.RequestParser()
space_args.add_argument('name', type=str, required=False, help='Name of the Space')
space_args.add_argument('uri', type=str, required=False, help='User URI part for SIP call to reach Space')
space_args.add_argument('secondaryUri', type=str, required=False, help='Secondary URI for SIP call to reach Space')
space_args.add_argument('passcode', type=str, required=False, help='Security code for this Space')
space_args.add_argument('defaultLayout', type=str, required=False, help='Default Layout for this Space',
                        choices=['automatic', 'allEqual', 'speakerOnly', 'telepresence', 'stacked', 'allEqualQuarters'],
                        default='automatic')


@api.route("/create_space")
class cms_create_space_api(Resource):
    # @api.expect(create_space_data)
    @api.expect(space_args)
    def post(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'],
             password=default_cms['password']):
        """
        Creates a new CMS Space.

        Use this method to add a new Space.

        * Send a JSON object with optional parameters, such as name, uri, secondaryUri, passcode,
          defaultLayout, etc in the request body.

        ```
        {
            "name": "Name of the Space",
            "uri": "User URI part for SIP call to reach Space",
            "secondaryUri": "Secondary URI for SIP call to reach Space",
            "passcode": "The security code for this Space",
            "defaultLayout": "The default layout to be used for new call legs in this Space.
                            May be:  automatic | allEqual | speakerOnly | telepresence | stacked | allEqualQuarters"
        }
        ```

        * Returns a dictionary with a 'success' (boolean) element.  If success is true, then the ID of
          the new Space is returned in the 'id' key.  Otherwise, a 'message' element will contain error information.
        """

        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.create_coSpace(payload=self.api.payload)


get_spaces_args = reqparse.RequestParser()
get_spaces_args.add_argument('filter', type=str, required=False, help='Search string')
get_spaces_args.add_argument('limit', type=int, required=False, help='How many results to return. \
  Note that CMS has an internal limit of 10 even though a larger limit can be requested', default=10)
get_spaces_args.add_argument('offset', type=int, required=False,
                             help='Return results starting with the offset specified', default=0)


@api.route("/spaces")
class cms_spaces_api(Resource):
    @api.expect(get_spaces_args)
    def get(self):
        """
        Retrieves all CMS Spaces with optional filters.

        Use this method to retrieve a list of Spaces.  If no space ID is supplied, then all results are returned.
        The output can be filtered using the following query parameters supplied in the URL:

        * offset (int) - An "offset" and "limit" can be supplied to retrieve coSpaces other than the
          first “page" in the notional list
        * limit (int)
        * filter (str) - Supply “filter=<string>” in the URI to return just those coSpaces that match the filter

        For example:
        ```  https://portal/api/v1/spaces?filter=sales&limit=5```
        """

        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        result = cms.get_coSpaces(parameters=args)
        return jsonify(result)


@api.route("/space/<id>")
class cms_space_api(Resource):
    def get(self, id):
        """
        Retrieves a CMS Space by ID.
        """

        # base_url = '/api/v1/coSpaces'
        # args = request.args.to_dict()
        # result = cms_send_request(host=host, username=username, password=password, port=port,
        #                           base_url=base_url, id=id, parameters=args)
        # return jsonify(result)
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        result = cms.get_coSpace(id=id)
        return jsonify(result)

    @api.expect(space_args)
    def put(self, id):
        """
        Edits a CMS space
        """
        # base_url = '/api/v1/coSpaces'
        # result = cms_send_request(host=host, username=username, password=password, port=port,
        #                           base_url=base_url, id=id, body=self.api.payload, request_method='PUT')
        # return jsonify(result)
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        result = cms.update_coSpace(id=id, payload=self.api.payload)
        return jsonify(result)

    def delete(self, id):
        """
        Removes a CMS space
        """
        # base_url = '/api/v1/coSpaces'
        # result = cms_send_request(host=host, username=username, password=password, port=port,
        #                           base_url=base_url, id=id, request_method='DELETE')
        # return jsonify(result)
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        result = cms.delete_coSpace(id=id)
        return jsonify(result)
