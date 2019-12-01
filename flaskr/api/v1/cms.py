from flask import jsonify
from flask import request
from flask import Blueprint
from flask_restplus import Namespace, Resource, fields
from flaskr.cms.v1.cms import CMS

api = Namespace('cms', description='Cisco Meeting Server REST API')

default_cms = {
    'host': 'cms1a.pod31.col.lab',
    'port': 8443,
    'username': 'admin',
    'password': 'c1sco123'
}

system_status_data = api.model('CMS System Status', {
    'host': fields.String(description='CMS host/IP', default=default_cms['host'], required=False),
    'port': fields.Integer(description='port', default=default_cms['port'], required=False),
    'username': fields.String(description='CMS API user name', default=default_cms['username'], required=False),
    'password': fields.String(description='CMS API user password', default='********', required=False),
})

@api.route("/system_status")
class cms_system_status_api(Resource):
    def get(self):
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.get_system_status()

# @api.route("/system_status")
# class cms_system_status_api(Resource):
#     def get(self):
#         """
#         Retrieves CMS system status.

#         Use this method to query for the CMS system status.
#         """
#         base_url = '/api/v1/system/status'
#         result = cms_send_request(host=default_cms['host'], port=default_cms['port'], username=default_cms['username'],
#                                   password=default_cms['password'], base_url=base_url)
#         return jsonify(result)


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


# @api.route("/version")
# class cms_version_api(Resource):
#     # @api.expect(system_status_data)
#     def get(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
#         """
#         Retrieves the version of the CMS system software.

#         Use this method to query for the CMS software version.
#         """
#         base_url = '/api/v1/system/status'
#         result = cms_send_request(
#             host=host, username=username, password=password, port=port, base_url=base_url)
#         if result['success']:
#             try:
#                 result = {
#                     'success': True, 'version': result['response']['status']['softwareVersion']}
#             except KeyError:
#                 pass
#         return jsonify(result)


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

        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.create_coSpace(payload=self.api.payload)

# @api.route("/create_space")
# class cms_create_space_api(Resource):
#     @api.expect(create_space_data)
#     def post(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'], password=default_cms['password']):
#         """
#         Creates a new CMS Space.

#         Use this method to add a new Space.

#         * Send a JSON object with optional parameters, such as name, uri, secondaryUri, passcode, defaultLayout, etc in the request body.

#         ```
#         {
#             "name": "Name of the Space",
#             "uri": "User URI part for SIP call to reach Space",
#             "secondaryUri": "Secondary URI for SIP call to reach Space",
#             "passcode": "The security code for this Space",
#             "defaultLayout": "The default layout to be used for new call legs in this Space.  May be:  allEqual | speakerOnly | telepresence | stacked"
#         }
#         ```

#         * Returns a dictionary with a 'success' (boolean) element.  If success is true, then the ID of the new Space is returned in the 'id' key.  Otherwise, a 'message element will contain error information.
#         """
#         base_url = '/api/v1/coSpaces'
#         result = cms_send_request(host=host, username=username, password=password, port=port, base_url=base_url, body=self.api.payload, request_method='POST')

#         return jsonify(result)


@api.route("/spaces")
class cms_spaces_api(Resource):
    def get(self):
        """
        Retrieves all CMS Spaces with optional filters.

        Use this method to retrieve a list of Spaces.  If no space ID is supplied, then all results are returned.
        The output can be filtered using the following query parameters supplied in the URL:

        * offset (int) - An "offset" and "limit" can be supplied to retrieve coSpaces other than the first “page" in the notional list
        * limit (int)
        * filter (str) - Supply “filter=<string>” in the URI to return just those coSpaces that match the filter
        * tenantFilter (str) - Supply tenantFilter=<tenant id> to return just those coSpaces associated with that tenant
        * callLegProfileFilter - Supply callLegProfileFilter=<call leg profile id> to return just those coSpaces using that call leg profile
        
        For example:
        ```  https://portal/spaces?filter=sales&limit=5```
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

        Use this method to retrieve a list of Spaces.  If no space ID is supplied, then all results are returned.
        The output can be filtered using the following query parameters supplied in the URL:

        * offset (int) - An "offset" and "limit" can be supplied to retrieve coSpaces other than the first “page" in the notional list
        * limit (int)
        * filter (str) - Supply “filter=<string>” in the URI to return just those coSpaces that match the filter
        * tenantFilter (str) - Supply tenantFilter=<tenant id> to return just those coSpaces associated with that tenant
        * callLegProfileFilter - Supply callLegProfileFilter=<call leg profile id> to return just those coSpaces using that call leg profile
        
        For example:
        ```  https://portal/spaces?filter=sales&limit=5```
        """

        # base_url = '/api/v1/coSpaces'
        # args = request.args.to_dict()
        # result = cms_send_request(host=host, username=username, password=password, port=port, base_url=base_url, id=id, parameters=args)
        # return jsonify(result)
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        result = cms.get_coSpace(id=id)
        return jsonify(result)

    def put(self, id):
        """
        Edits a CMS space
        """
        # base_url = '/api/v1/coSpaces'
        # result = cms_send_request(host=host, username=username, password=password, port=port, base_url=base_url, id=id, body=self.api.payload, request_method='PUT')
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
        # result = cms_send_request(host=host, username=username, password=password, port=port, base_url=base_url, id=id, request_method='DELETE')
        # return jsonify(result)
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        result = cms.delete_coSpace(id=id)
        return jsonify(result)


# @api.route("/location/<path:location>")
# class cms_generic_api(Resource):
#     def get(self, location, host=default_cms['host'], port=default_cms['port'],
#             username=default_cms['username'], password=default_cms['password']):
#         """
#         Generic GET to Unity Connection, given location url/path.
#         """

#         base_url = '/' + location
#         args = request.args.to_dict()
#         result = cms_send_request(host=host, username=username, password=password, port=port,
#                                   base_url=base_url, parameters=args)

#         return result

#     def post(self, location, host=default_cms['host'], port=default_cms['port'],
#              username=default_cms['username'], password=default_cms['password']):
#         """
#         Generic POST (create) to Unity Connection, given location url/path.  
#         """

#         base_url = '/' + location
#         args = request.args.to_dict()

#         result = cms_send_request(host=host, username=username, password=password, port=port,
#                                   base_url=base_url, parameters=args, body=self.api.payload,
#                                   request_method='POST')

#         return result

#     def put(self, location, host=default_cms['host'], port=default_cms['port'],
#             username=default_cms['username'], password=default_cms['password']):
#         """
#         Generic PUT (update) to Unity Connection, given location url/path.  
#         """

#         base_url = '/' + location
#         result = cms_send_request(host=host, username=username, password=password, port=port,
#                                   base_url=base_url, id=id, body=self.api.payload, request_method='PUT')

#         return result

#     def delete(self, location, host=default_cms['host'], port=default_cms['port'],
#                username=default_cms['username'], password=default_cms['password']):
#         """
#         Generic DELETE to Unity Connection, given location url/path.
#         """

#         base_url = '/' + location
#         result = cms_send_request(host=host, username=username, password=password, port=port,
#                                   base_url=base_url, request_method='DELETE')

#         return result
