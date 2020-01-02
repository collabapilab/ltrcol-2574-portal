from flask import request
from flask_restplus import Namespace, Resource, reqparse
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
        """
        Retrieves CMS system status.
        """
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
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
            return cms_status['response']['status']['softwareVersion']
        return cms_status


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
    @api.expect(space_args)
    def post(self, host=default_cms['host'], port=default_cms['port'], username=default_cms['username'],
             password=default_cms['password']):
        """
        Creates a new CMS Space.
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.create_coSpace(payload=args)


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
        Retrieves CMS Spaces.
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.get_coSpaces(parameters=args)


@api.route("/space/<id>")
class cms_space_api(Resource):
    def get(self, id):
        """
        Retrieves a CMS Space by object id.
        """
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        return cms.get_coSpace(id=id)

    @api.expect(space_args)
    def put(self, id):
        """
        Edits a CMS space by object id
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        return cms.update_coSpace(id=id, payload=args)

    def delete(self, id):
        """
        Removes a CMS space by object id
        """
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        return cms.delete_coSpace(id=id)
