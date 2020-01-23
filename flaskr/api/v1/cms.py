from flask import request
from flask_restplus import Namespace, Resource
from flaskr.api.v1.config import default_cms, default_cucm
from flaskr.cms.v1.cms import CMS
from flaskr.uds.v1.uds import UDS
from flaskr.api.v1.parsers import cms_spaces_get_args
from flaskr.api.v1.parsers import cms_spaces_post_args

api = Namespace('cms', description='Cisco Meeting Server REST API')

myCMS = CMS(default_cms['host'], default_cms['username'],
          default_cms['password'], port=default_cms['port'])
myCUCMuds = UDS(default_cucm['host'])


@api.route("/version")
class cms_version_api(Resource):
    def get(self):
        """
        Retrieves the version of the CMS system software.
        """
        # Retrieve the CMS system/status
        cms_status = myCMS._cms_request("system/status")
        if cms_status['success']:
            # Return only the version component
            return cms_status['response']['status']['softwareVersion']
        return cms_status


def match_space_uri(space_list, uri):
    """
    Searches a list of coSpaces and returns the id of the first coSpace that matches 
    either the URI or Secondary URI (if present) of the coSpace. 
    If neither is matched, return None.
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


def get_coSpace_id(userid):
    '''
    Returns the coSpace object ID given a user ID.
    Since CMS searching/filtering does not allow for an exact-match option, this function
    will search using the userid as a filter and then search through all results to find
    an exact match, if present.  
    Furthermore, any query may only return a subset of matches, therefore this function
    implements paging so as to examine all matches.  
    
    :param userid: (string)  UserID which will correspond to the coSpace URI or secondaryURI.

    :returns: Dictionary with keys: 'success' (bool), 'message' (str), and 'response' (str).
              The 'response' key will have the id, if available.
    '''

    params = {'filter': userid, 'offset': 0}

    # Retrieve a list of coSpaces, using the userid as the filter
    matched_spaces = myCMS._cms_request("coSpaces", parameters=params)
    try:
        # @total indicates the total number of matches, even if less coSpaces were returned in matched_spaces
        total_matches = int(matched_spaces['response']['coSpaces']['@total'])

        # Check if the total # of matches equals the number coSpaces in matched_spaces
        if total_matches == len(matched_spaces['response']['coSpaces']['coSpace']):
            id = match_space_uri(space_list=matched_spaces['response']['coSpaces']['coSpace'], uri=userid)
            if id:
                return {'success': True, 'message': 'Found Space for  "{}"'.format(userid), 'response': id}

        # The list of matches is not 0; we did not get a complete result from our first query
        elif total_matches > 0:
            all_spaces = matched_spaces['response']['coSpaces']['coSpace']

            while total_matches > len(all_spaces):
                id = match_space_uri(space_list=matched_spaces['response']['coSpaces']['coSpace'], uri=userid)
                if id:
                    return {'success': True, 'message': 'Found Space for  "{}"'.format(userid), 'response': id}
                # Adjust the offset to the total number of elements found so far
                params['offset'] = len(all_spaces)
                # Get another "page" using the adjusted offet in the params
                matched_spaces = myCMS._cms_request("coSpaces", parameters=params)
                # Re-read total_matches, in case something was deleted between our queries
                total_matches = int(matched_spaces['response']['coSpaces']['@total'])
                all_spaces += matched_spaces['response']['coSpaces']['coSpace']
    except KeyError:
        pass
    return {'success': False, 'message': 'Could not find a Space for user "{}"'.format(userid), 'response': ''}


@api.route("/spaces/<userid>")
@api.param('userid', 'The user ID associated with the Space')
class cms_spaces_api(Resource):
    def get(self, userid):
        """
        Retrieves a CMS Space by user id.
        """
        id = get_coSpace_id(userid=userid)
        if id['success']:
            return myCMS._cms_request(("coSpaces/" + id['response']))
        else:
            return id

    @api.expect(cms_spaces_post_args)
    def post(self, userid):
        """
        Creates a CMS space by user id
        """
        # Read available arguments: name, uri, secondaryUri, passcode, defaultLayout
        args = cms_spaces_post_args.parse_args()

        # Look up user via CUCM UDS
        user = myCUCMuds.get_user(userid)

        if user['success']:
            payload = {}
            if user['num_found'] == 1:
                payload['name'] = "{}'s Space".format(user['response']['displayName'])
                payload['uri'] = user['response']['userName']
                payload['secondaryUri'] = user['response']['phoneNumber']
                # Overwrite payload with whatever values were passed via args
                payload.update(args)

                return myCMS._cms_request("coSpaces", payload=payload, http_method='POST')
            else:
                return {'success': False,
                        'message': 'Found {} users with userid "{}"'.format(
                                    user['num_found'], userid)}
        else:
            # User lookup failed completely
            return user

    @api.expect(cms_spaces_post_args)
    def put(self, userid):
        """
        Edits a CMS space by object id
        """
        # Read available arguments: name, uri, secondaryUri, passcode, defaultLayout
        args = cms_spaces_post_args.parse_args()

        id = get_coSpace_id(userid=userid)
        if id['success']:
            return myCMS._cms_request("coSpaces/" + id['response'], payload=args, http_method='PUT')
        return id

    def delete(self, userid):
        """
        Removes a CMS space by user id
        """
        id = get_coSpace_id(userid=userid)
        if id['success']:
            return myCMS._cms_request("coSpaces/" + id['response'], http_method="DELETE")
        return id
