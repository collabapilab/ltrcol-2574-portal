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

function get_cms_version() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cms/version'
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

function enable_cms() {
    var username = $('#owner_id').html();

    $('#cms_div').removeClass("border-left-danger");
    $('#cms_div').addClass("border-left-info");
    $('#cms_status').html("Enabling...");

    add_cms_space(username).then(function() {
        post_wbxt_notification("Meeting Room Enabled for " + username);
        check_cms_status();
    });
}

function disable_cms() {
    var username = $('#owner_id').html();

    $('#cms_div').removeClass("border-left-success");
    $('#cms__div').addClass("border-left-info");
    $('#cms_status').html("Disabling...");

    remove_cms_space(username).then(function() {
        post_wbxt_notification("Meeting Room Disabled for " + username);
        check_cms_status();
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