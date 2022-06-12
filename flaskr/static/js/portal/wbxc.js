function wbx_get_user(username) {
    console.log('getting Webex user ' + username)
    return $.ajax({
		type: 'GET',
		url: '/api/v1/wbxc/user/' + username
	});
}

function wait_for_delete_done(count) {
    console.log("entering wait_for_delete_done")
    var username = $('#username').val();
    console.log("checking to see if delete was completed. Count = " + count)

    if (count > 5) {
        return {'done': true, 'count': count};
    }

    count++;

    console.log("Searching for " + username);
    if (username !== "") {
        find_user(username).then(function(data) {
            if (data['success'] == true) {
                console.log(data);
                if (data['phonesystem'] == 'Webex Calling') {
                    console.log("user still found in wxc... checking again...");
                    result = wait_for_delete_done(count);
                    console.log(result);
                    return result;
                } else {
                    console.log("user not found in wxc. stop waiting.")
                    user_search();
                    return {'done': true, 'count': count};
                }
                
            } else {
                console.log(data);
                return {'done': false, 'count': count};
            }
        });
    }

    console.log("exiting wait_for_delete_done");
    return {'done': true, 'count': count};
}

function wbx_display_user_data(user_data) {
    var name = user_data['displayName'];
    try {
        var userid = user_data['emails'][0];
    } catch {
        var userid = '';
    }

    wbx_id = atob(user_data['id']).replace('ciscospark://us/PEOPLE/', "");
    xlaunch_uri = 'https://admin.webex.com/manage-users/users/' + wbx_id + '/calling'
    console.log(xlaunch_uri);
    user_data['xlaunch_uri'] = xlaunch_uri;
    
    var template = `
    <div> 
        <p><strong>Name:</strong> <span id="owner_name">{{displayName}}</span></p>
        <p><strong>Email Address:</strong> {{email}}</p>
        <p><strong>Extension:</strong> {{extension}}</p>
        <p><strong>Phone Number:</strong> {{phone_number}}</p>
        <p>&nbsp;</p>
    </div>
    <div class="container">
       <div class="row">
         <div class="col text-center">
            <p><a href="{{xlaunch_uri}}" target="_blank">Configure Calling Settings in Control Hub</a></p>
            <p>&nbsp;</p>
         </div>
       </div>
       <div class="row">
        <div class="col text-center">
            <a href="#" id="disable_wbxc_button" class="btn btn-danger btn-icon-split">
                <span class="icon text-white-50">
                    <i class="fas fa-arrow-right"></i>
                </span>
                <span class="text">Disable Webex Calling</span>
            </a>
        </div>
      </div>
    </div>


    <script>
        $('#disable_wbxc_button').click(function (e) {
            e.preventDefault();
            disable_wbxc("{{username}}");
            wait_for_delete_done(0);
            user_search();
        });

    </script>
    `;

    try {
        email = user_data['emails'][0];
        console.log(email)
        user_data['email'] = email;
        username = email.substring(0, email.lastIndexOf("@"));
        console.log(username);
        user_data['username'] = username;
    } catch {
        user_data['email'] = ''
    }

    try {
        user_data['phone_number'] = user_data['phoneNumbers'][0]['value']
    } catch {
        user_data['phone_number'] = 'None'
    }

    var html = Mustache.to_html(template, user_data);

    $('#user_card_title').html('User Details for ' + name + ' (' + userid + ')' );
    $('#user_card_body').html(html);
}


function wbx_display_user_no_calling(user_data) {
    var name = user_data['displayName'];
    try {
        var userid = user_data['emails'][0];
    } catch {
        var userid = '';
    }

    console.log(user_data);

    var template = `
    <div> 
        <p><strong>Name:</strong> <span id="owner_name">{{displayName}}</span></p>
        <p><strong>Email Address:</strong> {{email}}</p>
        <p><strong>Phone Number:</strong> <input style="display:inline; width:60%;" id="wxc_phone_number" type="text" class="form-control" value="{{phone_number}}"></p>
        <p>&nbsp;</p>
    </div>
    <div class="container">
      <div class="row">
        <div class="col text-center">
            <a href="#" id="enable_wbxc_button" class="btn btn-success btn-icon-split">
                <span class="icon text-white-50">
                    <i class="fas fa-arrow-right"></i>
                </span>
                <span class="text">Enable Webex Calling</span>
            </a>
        </div>
      </div>
    </div>


    <script>
        $('#enable_wbxc_button').click(function (e) {
            e.preventDefault();
            enable_wbxc("{{username}}").then(function(data) {
                if (data['success'] == true) {
                    user_search();
                } else {
                    $('#toast-body').html(data['message']);
                    $('#status_toast').toast('show');
                }
            });
        });

    </script>
    `;

    try {
        email = user_data['emails'][0];
        console.log(email)
        user_data['email'] = email;
        username = email.substring(0, email.lastIndexOf("@"));
        console.log(username);
        user_data['username'] = username;
    } catch {
        user_data['email'] = ''
    }

    try {
        user_data['phone_number'] = user_data['phoneNumbers'][0]['value']
    } catch {
        user_data['phone_number'] = ''
    }

    var html = Mustache.to_html(template, user_data);

    $('#user_card_title').html('User Details for ' + name + ' (' + userid + ')' );
    $('#user_card_body').html(html);
}



function wbx_user_search() {
    username = $('#username').val();

    console.log("Searching for " + username);
    if (username !== "") {
        wbx_get_user(username).then(function(data) {
            if (data['success'] == true) {
                user_data = data['user_data'];
                console.log(user_data);
                wbx_display_user_data(user_data);
            } else {
                $('#toast-body').html(data['message']);
                $('#status_toast').toast('show');
            }
        });
    }
}

function enable_wbxc(username) {
    console.log("enable_wbxc for " + username);
    phone_number = $('#wxc_phone_number').val();
    console.log(phone_number);
    phone_number = encodeURIComponent(phone_number);
    license = encodeURIComponent('Webex Calling - Professional');
    url = '/api/v1/wbxc/user/enable/' + username + '?' + license + '&phone_number=' + phone_number
    console.log(url);
    return $.ajax({
		type: 'PUT',
		url: url
	});
}

function disable_wbxc(username) {
    console.log("disable_wbxc for " + username);
    return $.ajax({
		type: 'PUT',
		url: '/api/v1/wbxc/user/disable/' + username
	});
}