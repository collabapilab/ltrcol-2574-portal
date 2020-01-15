function get_cuc_user(username) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cuc/users/' + username
	});
}

function add_cuc_user(username) {
    return $.ajax({
		type: 'POST',
		url: '/api/v1/cuc/users/' + username
	});
}

function remove_cuc_user(username) {
    console.log("Removing CUC User " + username);
    return $.ajax({
		type: 'DELETE',
		url: '/api/v1/cuc/users/' + username
	});
}

function get_cms_space(username) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cms/spaces/' + username
	});
}

function add_cms_space(username) {
    return $.ajax({
		type: 'POST',
		url: '/api/v1/cms/spaces/' + username
	});
}

function remove_cms_space(username) {
    return $.ajax({
		type: 'DELETE',
		url: '/api/v1/cms/spaces/' + username
	});
}

function get_cuc_version() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cuc/version'
	});
}

function get_cms_version() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cms/version'
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

function check_cms_status() {
    var username = $('#owner_id').html();

    get_cms_space(username).then(function(result) {
        var cms_enabled = null;

        if (result['success'] == true) {
            cms_enabled = true;
        } else {
            cms_enabled = false;
        }
        
        if (cms_enabled !== null) {
            
            $('#cms_div').removeClass("border-left-info");
            $('#cms_div').removeClass("border-left-danger");
            $('#cms_div').removeClass("border-left-success");
            $('#cms_enable_btn').addClass("d-none");
            $('#cms_disable_btn').addClass("d-none");

            switch (cms_enabled) {
                case true:
                    $('#cms_status').html("Enabled");
                    $('#cms_div').addClass("border-left-success");
                    $('#cms_disable_btn').removeClass("d-none");
                    break;
                case false:
                    $('#cms_status').html("Disabled");
                    $('#cms_div').addClass("border-left-danger");
                    $('#cms_enable_btn').removeClass("d-none");
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
        check_vm_status();
    });
}

function disable_vm() {
    var username = $('#owner_id').html();

    $('#vm_div').removeClass("border-left-success");
    $('#vm_div').addClass("border-left-info");
    $('#voicemail_status').html("Disabling...");

    remove_cuc_user(username).then(function(result) {
        console.log(result);
        check_vm_status();
    });
}

function enable_cms() {
    var username = $('#owner_id').html();

    $('#cms_div').removeClass("border-left-danger");
    $('#cms_div').addClass("border-left-info");
    $('#cms_status').html("Enabling...");

    add_cms_space(username).then(function() {
        check_cms_status();
    });
}

function disable_cms() {
    var username = $('#owner_id').html();

    $('#cms_div').removeClass("border-left-success");
    $('#cms__div').addClass("border-left-info");
    $('#cms_status').html("Disabling...");

    remove_cms_space(username).then(function() {
        check_cms_status();
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

function update_cms_version() {
    get_cms_version().then(function(result) {
        console.log(result);
        if (result != null) {
            version = result;
        } else {
            version = "unknown";
        }

        $('#cms_version').html(version);
    });
}