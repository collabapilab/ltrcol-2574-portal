function get_cuc_user(username) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cuc/users/' + username
	});
}

function add_cuc_user(username) {
    return $.ajax({
		type: 'PUT',
		url: '/api/v1/core/vmusers/' + username
	});
}

function remove_cuc_user(username) {
    console.log("Removing CUC User " + username);
    return $.ajax({
		type: 'DELETE',
		url: '/api/v1/core/vmusers/' + username
	});
}

function get_cuc_version() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cuc/version'
	});
}

function check_vm_status() {
    var username = $('#owner_id').html();

    get_cuc_user(username).then(function(result) {
        var vm_enabled = null;

        console.log(result);

        if (result['success'] == true) {
            if (result['response']['@total'] == '0') {
                vm_enabled = false;
            } else {
                vm_enabled = true;
            }
        } else {
            console.log("Error attempting to retrieve user.");
            console.log(result);
        }
        
        if (vm_enabled !== null) {
            
            $('#vm_div').removeClass("border-left-info");
            $('#vm_div').removeClass("border-left-danger");
            $('#vm_div').removeClass("border-left-success");
            $('#vm_enable_btn').addClass("d-none");
            $('#vm_disable_btn').addClass("d-none");

            switch (vm_enabled) {
                case true:
                    $('#voicemail_status').html("Enabled");
                    $('#vm_div').addClass("border-left-success");
                    $('#vm_disable_btn').removeClass("d-none");
                    break;
                case false:
                    $('#voicemail_status').html("Disabled");
                    $('#vm_div').addClass("border-left-danger");
                    $('#vm_enable_btn').removeClass("d-none");
                    break;
            }
        }
    });
}

function enable_vm() {
    var username = $('#owner_id').html();

    $('#vm_div').removeClass("border-left-danger");
    $('#vm_div').addClass("border-left-info");
    $('#voicemail_status').html("Enabling...");

    add_cuc_user(username).then(function() {
        post_wbxt_notification("Voicemail Enabled for " + username);
        check_vm_status();
    });
}

function disable_vm() {
    var username = $('#owner_id').html();

    $('#vm_div').removeClass("border-left-success");
    $('#vm_div').addClass("border-left-info");
    $('#voicemail_status').html("Disabling...");

    remove_cuc_user(username).then(function(result) {
        post_wbxt_notification("Voicemail Disabled for " + username);
        check_vm_status();
    });
}

function update_cuc_version() {
    get_cuc_version().then(function(result) {
        console.log(result);
        if (result['success'] == true) {
            version = result['response']['version'];
        } else {
            version = "unknown";
        }

        $('#cuc_version').html(version);
    });
}

