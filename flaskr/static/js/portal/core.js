function find_user(username) {
    console.log('finding user ' + username)
    return $.ajax({
		type: 'GET',
		url: '/api/v1/core/users/' + username
	});
}



function user_search() {
    var username = $('#username').val();

    console.log("Searching for " + username);
    if (username !== "") {
        find_user(username).then(function(data) {
            if (data['success'] == true) {
                if (data['phonesystem'] == 'Unified CM') {
                    console.log('User Found in Unified CM');
                    user_data = data['cucm_user_data'];
                    show_ucm_user_data(user_data);
                } else if (data['phonesystem'] == 'Webex Calling') {
                    console.log('User Found in Webex Calling');
                    user_data = data['wbxc_user_data'];
                    clear_user_fields();
                    wbx_display_user_data(user_data);
                } else if (data['phonesystem'] == 'User not found on either system') {
                    console.log('User Found in Neither');
                    $('#toast-body').html("User not found in UCM or Webex.");
                    $('#status_toast').toast('show');
                } else if (data['phonesystem'] == 'Both Webex Calling and Unified CM') {
                    console.log('User Found in Both UCM and Webex');
                    user_data = data['wbxc_user_data']['user_data'];
                    console.log(user_data);
                    clear_user_fields();
                    wbx_display_user_data(user_data);
                } else if (data['phonesystem'] == 'Neither Webex Calling nor Unified CM') {
                    var ucm_user = data['is_ucm_user'];
                    var ucm_enabled = data['is_ucm_enabled'];
                    var wbxc_user = data['is_wbxc_user'];
                    var wbxc_enabled = data['is_wbxc_enabled'];

                    if (wbxc_user && !wbxc_enabled) {
                        wbx_get_user(username).then(function(data) {
                            if (data['success'] == true) {
                                user_data = data['user_data'];
                                clear_user_fields();
                                console.log(user_data);
                                wbx_display_user_no_calling(user_data)        
                            } else {
                                $('#toast-body').html(data['message']);
                                $('#status_toast').toast('show');
                            }
                        });
                    } else if (ucm_user) {
                        user_data = data['ucm_user_data'];
                        clear_user_fields();
                        ucm_display_user_no_calling(user_data);
                    }
                }
            } else {
                console.log(data);
                $('#toast-body').html(data['message']);
                $('#status_toast').toast('show');
            }
        });
    }
}
