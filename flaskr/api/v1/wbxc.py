import json
from flask import request, jsonify
from flask_restx import Namespace, Resource
from flaskr.api.v1.config import WBX_USER_ACCESS_TOKEN, DOMAIN
from flaskr.api.v1.parsers import wbxc_enable_user_args
from wxc_sdk import WebexSimpleApi
from wxc_sdk.rest import RestError

api = Namespace('wbxc', description='Webex Calling APIs')

# Create the Webex Calling API connection object
wxc_api = WebexSimpleApi(tokens=WBX_USER_ACCESS_TOKEN)


def to_email(user_id):
    # Return the email address given the user id
    return user_id + '@' + DOMAIN


def get_person_det(email):
    """
    Searches the Webex Persons by email address, if exactly one is found, look up and return
    the Person details, including Webex Calling Data.
    """
    # Search all users and find the one containing the email
    wxc_people_list = list(wxc_api.people.list(email=email))
    if len(wxc_people_list) == 1:
        # Look up user details, including Webex Calling data; the wxc_people_list has exactly one entry at index[0]
        my_person = wxc_api.people.details(person_id=wxc_people_list[0].person_id, calling_data=True)
        return my_person


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
            if not target_person:
                return jsonify({'success': False, 'message': f'User not found with email {to_email(userid)}'})
            return jsonify({'success': True,
                            'message': f'Successfully found user {userid}',
                            'user_data': json.loads(target_person.json())})

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
            target_person = get_person_det(to_email(userid))
            if not target_person:
                return jsonify({'success': False, 'message': f'User not found with email {to_email(userid)}'})

            # Search all licenses and find the one matching the specified license
            license_list = list(wxc_api.licenses.list())
            wxc_pro_license = get_lic_by_name(licenses=license_list, name='Webex Calling - Professional')
            ucm_license = get_lic_by_name(licenses=license_list, name='On-Prem UCM Calling')

            # Find the location provided location name
            target_location = wxc_api.locations.by_name(args['location'])
            if not target_location:
                return jsonify({'success': False, 'message': f'Location not found: {args["location"]}'})

            # Look up the user's phone number (set in Active Directory and synched to the Webex work number)
            target_tn = None
            for num in target_person.phone_numbers:
                if num.number_type == 'work':
                    target_tn = num.value
            if not target_tn:
                return jsonify({'success': False,
                                'message': f'Phone number not configured for user: {userid}'})

            # Check if user is already enabled for Webex Calling (i.e. they have a location_id assigned)
            if not target_person.location_id:
                # Append the Webex license and remove the On-Prem UCM Calling, if present
                target_person.licenses.append(wxc_pro_license.license_id)
                if ucm_license.license_id in target_person.licenses:
                    target_person.licenses.remove(ucm_license.license_id)

                # Set the user's location id
                target_person.location_id = target_location.location_id

                # Update the user
                wxc_api.people.update(person=target_person, calling_data=True)

                return jsonify({'success': True,
                                'message': f"Successfully enabled Webex Calling for user {userid} on "
                                           f"location {args['location']} with number {target_tn}",
                                'user_data': json.loads(target_person.json())})

            else:
                if target_location.location_id == target_person.location_id:
                    return jsonify({'success': True, 'message': f"User {userid} already enabled for Webex Calling in "
                                                                f"location {args['location']}"})
                else:
                    return jsonify({'success': False, 'message': f"User {userid} already enabled for Webex Calling "
                                                                 f"but not in location {args['location']}"})
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
                # Search all licenses and find the one matching the specified license
                license_list = list(wxc_api.licenses.list())
                wxc_pro_license = get_lic_by_name(licenses=license_list, name='Webex Calling - Professional')
                ucm_license = get_lic_by_name(licenses=license_list, name='On-Prem UCM Calling')

                # Disable Webex Calling by removing the webex calling license (this will automatically clear the
                # location and the WxC phone number) and re-add the on-prem calling license
                if wxc_pro_license:
                    target_person.licenses.remove(wxc_pro_license.license_id)
                    if ucm_license:
                        if ucm_license.license_id not in target_person.licenses:
                            target_person.licenses.append(ucm_license.license_id)

                    # Update the user, this removes the license and location
                    target_person = wxc_api.people.update(person=target_person, calling_data=True)

                    result = {'success': True,
                              'message': f'Successfully disabled Webex Calling for user {userid}',
                              'user_data': json.loads(target_person.json())}
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
