import logging
from flask import request, jsonify
from flask_restx import Namespace, Resource
from flaskr.api.v1.parsers import wbxc_enable_user_args
from os import getenv
from wxc_sdk.rest import RestError
from .service_app import ServiceApp

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s')
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
# Change to DEBUG for detailed REST interaction output
logging.getLogger('wxc_sdk.rest').setLevel(logging.INFO)

log = logging.getLogger(__name__)

api = Namespace('wbxc', description='Webex Calling APIs')


def to_email(user_id):
    # Return the email address given the user id
    return user_id + '@' + getenv('DOMAIN')


def get_person_det(email):
    """
    Searches the Webex Persons by email address, if exactly one is found, look up and return
    the Person details, including Webex Calling Data.
    """
    # Create a Service App instance
    pass


def get_lic_by_name(licenses, name):
    """
    Searches Webex licenses and returns the license if a matching "name" is found.
    """
    for lic in licenses:
        if lic.name == name:
            return lic



@api.route("/user/<string:userid>")
@api.param('userid', 'The user id of the user to be returned')
class wbxc_user_api(Resource):

    def get(self, userid):
        """
        Retrieve a user in WbxC by user id.
        """
        try:
            # Get the detailed user by email
            target_person = get_person_det(to_email(userid))

        except Exception as e:
            # Return any API error that may have been raised
            return jsonify({'success': False, 'message': str(e)})


@api.route('/user/enable/<string:userid>')
@api.param('userid', 'The user id of the user to be enabled')
class wbxc_user_enable_api(Resource):

    @api.expect(wbxc_enable_user_args, validate=True)
    def put(self, userid):
        """
        Enable a Person for Webex Calling by user ID.
        """
        try:
            # Read all arguments
            args = wbxc_enable_user_args.parse_args(request)

            # Get the person details for a user with this email address

            # Check if user is already enabled for Webex Calling (i.e. they have a location_id assigned)

        # Return any REST error that may have been raised
        except RestError as e:
            return jsonify({'success': False, 'message': str(e)})


@api.route('/user/disable/<string:userid>')
@api.param('userid', 'The user id of the user to be disabled')
class wbxc_user_disable_api(Resource):

    def put(self, userid):
        """
        Disable a Webex Calling Person by user ID.
        """

        try:
            # Get the person details for a user with this email address
            target_person = get_person_det(to_email(userid))
            if not target_person:
                return jsonify({'success': False, 'message': f'User not found with email {to_email(userid)}'})

            # Check if enabled for WxC
            if target_person.location_id:
                # Create a Service App instance
                sa = ServiceApp()

                # Search all licenses and find the one matching the specified license
                license_list = list(sa.api.licenses.list())
                wxc_pro_license = get_lic_by_name(licenses=license_list, name='Webex Calling - Professional')
                ucm_license = get_lic_by_name(licenses=license_list, name='Unified Communication Manager (UCM)')

                # Disable Webex Calling by removing the webex calling license (this will automatically clear the
                # location and the WxC phone number) and re-add the on-prem calling license
                if wxc_pro_license:
                    target_person.licenses.remove(wxc_pro_license.license_id)
                    if ucm_license:
                        if ucm_license.license_id not in target_person.licenses:
                            target_person.licenses.append(ucm_license.license_id)

                    # Update the user, this removes the license and location
                    target_person = sa.api.people.update(person=target_person, calling_data=True)

                    result = {'success': True,
                              'message': f'Successfully disabled Webex Calling for user {userid}',
                              'user_data': target_person.dict()}
                else:
                    result = {'success': False,
                              'message': f'Cannot enable Webex Calling for {userid}. Webex Calling - Professional '
                                         f'license not found.'}
            else:
                result = {'success': True,
                          'message': f'User {userid} already disabled for Webex Calling'}

            return jsonify(result)

        except RestError as e:
            # Return any REST error that may have been raised
            return jsonify({'success': False, 'message': str(e)})
