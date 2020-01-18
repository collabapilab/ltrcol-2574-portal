from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import default_cms, default_cucm
from flaskr.cms.v1.cms import CMS
from flaskr.uds.v1.uds import UDS
from flaskr.api.v1.parsers import cms_spaces_get_args
from flaskr.api.v1.parsers import cms_spaces_post_args

api = Namespace('cms', description='Cisco Meeting Server REST API')


@api.route("/system_status")
class cms_system_status_api(Resource):
    def get(self):
        """
        Retrieves CMS system status.
        """
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])

        return cms._cms_request("system/status")


@api.route("/version")
class cms_version_api(Resource):
    # @api.expect(system_status_data)
    def get(self):
        """
        Retrieves the version of the CMS system software.

        Use this method to query for the CMS software version.
        """
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        # Retrieve the CMS system/status
        cms_status = cms._cms_request("system/status")
        if cms_status['success']:
            # Return only the version component
            return cms_status['response']['status']['softwareVersion']
        return cms_status


def get_matched_uri(space_list, uri):
    """
    Returns pkid of the Space where the URI or Secondary URI match the searched uri.
    If neither is matched, return None.  Neither uri or secondaryUri are required
    Space settings, so we need to take that into account.
    """
    for space in space_list:
        try:
            # Check if the URI matches the current Space URI component
            if uri == space['uri']:
                return space['@id']
        except KeyError:
            pass
        try:
            # Check if the URI matches the current Space secondaryUri component
            if uri == space['secondaryUri']:
                return space['@id']
        except KeyError:
            pass
    return None


def get_coSpace_pkid(cms, userid):
    '''
    Return the coSpace object ID given a user ID.

    :param cms: (CMS) CMS object type
    :param userid: (string)  UserID which will correspond to the coSpace URI or secondaryURI.

    :returns: Dictionary with keys: 'success' (bool), 'message' (str), and 'response' (str).
                The 'response' key will have the pkid, if available.
    '''

    parameters = {'filter': userid, 'offset': 0}

    matched_spaces = cms._cms_request("coSpaces", parameters=parameters)
    try:
        total_matches = int(matched_spaces['response']['coSpaces']['@total'])

        if total_matches == len(matched_spaces['response']['coSpaces']['coSpace']):
            # Received all matches back
            pkid = get_matched_uri(space_list=matched_spaces['response']['coSpaces']['coSpace'], uri=userid)
            if pkid:
                return {'success': True, 'message': 'Found Space for  "{}"'.format(userid), 'response': pkid}
        elif total_matches > 0:
            # The list of results was not the complete set of results
            all_spaces = matched_spaces['response']['coSpaces']['coSpace']

            while total_matches > len(all_spaces):
                pkid = get_matched_uri(space_list=matched_spaces['response']['coSpaces']['coSpace'], uri=userid)
                if pkid:
                    return {'success': True, 'message': 'Found Space for  "{}"'.format(userid), 'response': pkid}
                parameters['offset'] = len(all_spaces)
                matched_spaces = cms._cms_request("coSpaces", parameters=parameters)
                all_spaces += matched_spaces['response']['coSpaces']['coSpace']
    except KeyError:
        pass
    return {'success': False, 'message': 'Could not find a Space for user "{}"'.format(userid), 'response': ''}


@api.route("/spaces")
class cms_spaces_api(Resource):

    @api.expect(cms_spaces_get_args)
    def get(self):
        """
        Retrieves all CMS Spaces.
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])
        return cms._cms_request("coSpaces", parameters=args)


@api.route("/spaces/<userid>")
@api.param('userid', 'The user ID associated with the Space')
class cms_space_api(Resource):
    def get(self, userid):
        """
        Retrieves a CMS Space by user id.
        """
        cms = CMS(default_cms['host'], default_cms['username'], default_cms['password'], port=default_cms['port'])
        # pkid = cms.get_coSpace_pkid(userid=userid)
        pkid = get_coSpace_pkid(cms, userid=userid)
        if pkid['success']:
            return cms._cms_request(("coSpaces/" + pkid['response']))
        else:
            return pkid

    @api.expect(cms_spaces_post_args)
    def post(self, userid):
        """
        Creates a CMS space by user id
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])

        cucm_uds = UDS(default_cucm['host'])
        user = cucm_uds.get_user(parameters={'username': userid})

        payload = {}
        if user['success']:
            if user['num_found'] == 1:
                payload['name'] = "{}'s Space".format(user['response']['users']['user'][0]['displayName'])
                payload['uri'] = user['response']['users']['user'][0]['userName']
                payload['secondaryUri'] = user['response']['users']['user'][0]['phoneNumber']
                # Overwrite payload with whatever values were passed via args
                payload.update(args)

                return cms._cms_request("coSpaces", payload=payload, http_method='POST')
            else:
                return {'success': False,
                        'message': 'Found {} users with userid "{}"'.format(
                                    user['num_found'], args['userid'])}
        else:
            # User lookup failed completely
            return user

    @api.expect(cms_spaces_post_args)
    def put(self, userid):
        """
        Edits a CMS space by object id
        """
        args = request.args.to_dict()
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])

        pkid = get_coSpace_pkid(cms, userid=userid)
        if pkid['success']:
            return cms._cms_request("coSpaces/" + pkid['response'], payload=args, http_method='PUT')
        return pkid

    def delete(self, userid):
        """
        Removes a CMS space by user id
        """
        cms = CMS(default_cms['host'], default_cms['username'],
                  default_cms['password'], port=default_cms['port'])

        pkid = get_coSpace_pkid(cms, userid=userid)
        if pkid['success']:
            return cms._cms_request("coSpaces/" + pkid['response'], http_method="DELETE")
        return pkid
