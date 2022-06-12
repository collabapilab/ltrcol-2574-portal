import json
from flask import request, jsonify
from flask_restx import Namespace, Resource
from flaskr.api.v1.config import wbx_user_access_token, domain, wbxc_license_name, extension_length
from flaskr.api.v1.parsers import wbxc_enable_user_args
from wxc_sdk import WebexSimpleApi
from wxc_sdk.rest import RestError


api = Namespace('wbxc', description='Webex Calling APIs')

# Create the Webex Calling API connection object
wxc_api = WebexSimpleApi(tokens=wbx_user_access_token)


def find_obj_by_key(search_list, search_item, key='name'):
    """
    Iterates through a search_list for a search_item, and either returns that item or False.
    The search_list can be a list or a generator consisting of dictionaries or class element types. Either the
    dictionary must have a 'name' (or other key specified in the key variable) or the class attribute must
    have the 'name' or specified key attribute.
    """
    if search_list:
        for item in search_list:
            if type(item) == dict:
                if eval('item[\'' + key + '\']') == search_item:
                    return item
            else:
                if eval('item.' + key) == search_item:
                    return item
    return False


def convert_person_to_json(person):
    """
    Takes a person object, converts it to a serialized JSON string using its own method, and then back to a JSON object.
    By doing so, all custom classes in the Person object will be changed to simple python data types.
    """
    return json.loads(person.json())


@api.route("/user/enable/<string:userid>")
@api.param('userid', 'The user id of the user to be enabled')
class wbxc_user_enable_api(Resource):

    @api.expect(wbxc_enable_user_args, validate=True)
    def put(self, userid):
        """
        Enable a user for Webex Calling given a user ID, a desired phone number, a Webex Calling location,
        and a Webex Calling License name.
        """
        try:
            args = wbxc_enable_user_args.parse_args(request)

            # Create the email address from the user id
            email = userid + '@' + domain

            # Search all users and find the one containing the email
            wxc_people_list = wxc_api.people.list(email=email)
            target_person = find_obj_by_key(search_list=wxc_people_list, search_item=email, key='emails[0]')
            if not target_person:
                return jsonify({'success': False, 'message': f'User not found with email: {email}'})

            # Look up user details, including Webex Calling data
            target_person = wxc_api.people.details(person_id=target_person.person_id, calling_data=True)
            if not target_person:
                return jsonify({'success': False, 'message': 'User details not found for email: {email}'})

            # Search all licenses and find the one matching the specified license
            wxc_licenses_list = wxc_api.licenses.list()
            target_license = find_obj_by_key(search_list=wxc_licenses_list, search_item=args['license'])
            if target_license:
                target_license_id = target_license.license_id
                # Ensure not all licenses are used up
                if target_license.consumed_units >= target_license.total_units:
                    return jsonify({'success': False, 'message': f'All licenses consumed: {args["license"]}'})
            else:
                return jsonify({'success': False, 'message': f'License not found: {args["license"]}'})

            # Search all locations and find the one matching the desired target location
            wxc_locations_list = wxc_api.locations.list()
            target_location = find_obj_by_key(search_list=wxc_locations_list, search_item=args['location'])
            if target_location:
                target_location_id = target_location.location_id
            else:
                return jsonify({'success': False, 'message': f'Location not found: {args["location"]}'})

            if not args['phone_number'] and not target_person.phone_numbers:
                return jsonify({'success': False,
                                'message': f'No phone number specified or configured for user {email}'})

            # Check if user is already enabled for Webex Calling (i.e. they have a location_id assigned)
            if not target_person.location_id:
                # get available numbers for the location
                available_numbers = wxc_api.telephony.phone_numbers(location_id=target_location_id, available=True)

                # Look for the requested phone_number to make sure it's available in the available phone numbers list
                avail_num = find_obj_by_key(available_numbers, args['phone_number'], key='phone_number')
                if avail_num:
                    # Check the phone_number is already configured for this user
                    target_nums = find_obj_by_key(search_list=target_person.phone_numbers,
                                                  search_item=args['phone_number'], key='value')
                    if not target_nums:
                        # Create a list with the new phone number
                        target_person.phone_numbers = [{"type": "work", "value": args['phone_number']}]

                    # Set the user's extension based on the last digits of the phone number
                    target_person.extension = args['phone_number'][-extension_length:]

                    # Append the Webex license
                    target_person.licenses.append(target_license_id)
                    # Set the user's location id
                    target_person.location_id = target_location_id

                    # Update the user
                    wxc_api.people.update(person=target_person, calling_data=True)

                    return jsonify({'success': True,
                                    'message': f"Successfully enabled {wbxc_license_name} for user {email} on "
                                               f"location {args['location']} with number {args['phone_number']}"})
                else:
                    return jsonify({'success': False, 'message': f"Phone number {args['phone_number']} not found "
                                                                 f"or not available in location {args['location']}"})

            else:
                if target_location_id == target_person.location_id:
                    return jsonify({'success': True, 'message': f"User {email} already enabled for Webex Calling in "
                                                                f"location {args['location']}"})
                else:
                    return jsonify({'success': False, 'message': f"User {email} already enabled for Webex Calling "
                                                                 f"but not in location {args['location']}"})
        # We need to catch the 403 / Forbidden Exception here
        except RestError as e:
            # Check if there was an incorrect "permission denied" returned.
            # If so, query the user to see if the changes have been applied.
            if e.response.status_code == 403:
                target_person_new = wxc_api.people.details(person_id=target_person.person_id, calling_data=True)
                if target_person_new.location_id == target_location_id:
                    return jsonify({'success': True,
                                    'message': f"Successfully enabled {wbxc_license_name} for user {email} on "
                                               f"location {args['location']} with number {args['phone_number']}",
                                    'user_data': convert_person_to_json(target_person_new)})

            # Return any REST error that may have been raised
            return jsonify({'success': False, 'message': str(e)})


@api.route("/user/disable/<string:userid>")
@api.param('userid', 'The user id of the user to be disabled')
class wbxc_user_disable_api(Resource):

    def put(self, userid):
        """
        Disable a Webex Calling user by user id. To do this, we must look up the user details, remove the
        license, and update that user.
        """

        try:
            # Create the email address from the user ID
            email = userid + '@' + domain

            # Search all users and find the one containing the desired email
            target_person = find_obj_by_key(search_list=wxc_api.people.list(), search_item=email, key='emails[0]')
            target_person = wxc_api.people.details(person_id=target_person.person_id, calling_data=True)

            # Check if enabled for WbxC
            if target_person.location_id:
                # Enabled for webex calling. Disable them by removing the webex calling license
                # This will automatically clear the location, extension, and the WbxC directory number
                wbxc_pro_license = find_obj_by_key(search_list=wxc_api.licenses.list(), search_item=wbxc_license_name)

                if wbxc_pro_license:
                    target_person.licenses.remove(wbxc_pro_license.license_id)

                    target_person = wxc_api.people.update(person=target_person, calling_data=True)
                    result = {'success': True,
                              'message': f"Successfully disabled {wbxc_license_name} license for user {email}"}
                else:
                    result = {'success': True,
                              'message': f"Webex Calling still configured for user {email}, but with a license"
                                         f"other than {wbxc_license_name}"}

            else:
                return jsonify({'success': True,
                                'message': f"User {email} already disabled for Webex Calling"})

        except RestError as e:
            # Check if there was an incorrect "permission denied" returned.
            # If so, query the user to see if the changes have been applied..
            if e.response.status_code == 403:
                target_person_new = wxc_api.people.details(person_id=target_person.person_id, calling_data=True)
                if not target_person_new.location_id:
                    return jsonify({'success': True,
                                    'message': f"Successfully disabled {wbxc_license_name} license for user {email}",
                                    'user_data': convert_person_to_json(target_person_new)})

            # Return any REST error that may have been raised
            return jsonify({'success': False, 'message': str(e)})


@api.route("/user/<string:userid>")
@api.param('userid', 'The user id of the user to be returned')
class wbxc_user_api(Resource):

    def get(self, userid):
        """
        Retrieve a user in WbxC by user id.
        """

        try:
            # Create the email address
            email = userid + '@' + domain

            # Search all users and find the one containing the desired email
            target_person = find_obj_by_key(search_list=wxc_api.people.list(), search_item=email, key='emails[0]')
            if target_person:
                # Retrieve all the user details
                target_person = wxc_api.people.details(person_id=target_person.person_id, calling_data=True)
                # Set the result. The person data must be converted to a string, so it can be serialized later.
                result = {'success': True,
                          'message': f'Successfully found user {email}',
                          'user_data': convert_person_to_json(target_person)}
            else:
                result = {'success': False,
                          'message': f'No user found with email {email}'}
            return jsonify(result)

        except Exception as e:
            # Return any API error that may have been raised
            result = {'success': False, 'message': str(e)}
            return jsonify(result)
