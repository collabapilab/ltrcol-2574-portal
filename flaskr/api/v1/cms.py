from flask import request
from flask_restx import Namespace, Resource
from flaskr.cms.v1.cms import CMS
from flaskr.uds.v1.uds import UDS
from flaskr.api.v1.parsers import cms_spaces_get_args
from flaskr.api.v1.parsers import cms_spaces_post_args
from os import getenv

api = Namespace('cms', description='Cisco Meeting Server REST API')

myCUCMuds = UDS(getenv('CUCM_HOSTNAME'))


@api.route("/version")
class cms_version_api(Resource):
    def get(self):
        """
        Retrieves the version of the CMS system software.
        """
        # Retrieve the CMS system/status
        pass


def match_space_uri(space_list, uri):
    """
    Searches a list of coSpaces and returns the id of the first coSpace that matches 
    either the URI or Secondary URI (if present) of the coSpace. 
    If neither is matched, return None.
    """
    pass


def get_coSpace_id(userid):
    '''
    Returns the coSpace object ID given a user ID and CMS object.
    Since CMS searching/filtering does not allow for an exact-match option, this function
    will search using the userid as a filter and then search through all results to find
    an exact match, if present.  
    Furthermore, any query may only return a subset of matches, therefore this function
    implements paging so as to examine all matches.  
    
    :param cms: (CMS) CMS object type
    :param userid: (string)  UserID which will correspond to the coSpace URI or secondaryURI.

    :returns: Dictionary with keys: 'success' (bool), 'message' (str), and 'response' (str).
              The 'response' key will have the id, if available.
    '''

    params = {'filter': userid, 'offset': 0}

    # Retrieve a list of coSpaces, using the userid as the filter


@api.route("/spaces/<userid>")
@api.param('userid', 'The user ID associated with the Space')
class cms_spaces_api(Resource):
    def get(self, userid):
        """
        Retrieves a CMS Space by user id.
        """
        # Look up user's id by userid
        pass

    @api.expect(cms_spaces_post_args)
    def post(self, userid):
        """
        Creates a CMS space by user id
        """
        # Read available arguments: name, uri, secondaryUri, passcode, defaultLayout
        args = cms_spaces_post_args.parse_args()

        # Look up user via CUCM UDS

    @api.expect(cms_spaces_post_args)
    def put(self, userid):
        """
        Edits a CMS space by object id
        """
        # Read available arguments: name, uri, secondaryUri, passcode, defaultLayout
        args = cms_spaces_post_args.parse_args()        

        # Look up user's id by userid

    def delete(self, userid):
        """
        Removes a CMS space by user id
        """
        # Look up user's id by userid
        pass
