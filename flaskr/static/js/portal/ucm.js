function get_perfmon_data() {
	return $.ajax({
		type: 'POST',
		url: '/api/v1/cucm/perfmon',
        data: JSON.stringify(
        {
            "perfmon_counters": [
              "\\\\vnt-cm1b.cisco.com\\Cisco CallManager\\RegisteredHardwarePhones",
              "\\\\vnt-cm1b.cisco.com\\Cisco CallManager\\CallsActive",
              "\\\\vnt-cm1b.cisco.com\\Cisco CallManager\\CallsCompleted"
            ]
        }),
        contentType: "application/json",
	});
}

function insert_device(device_name, device_description, device_model, clid_name, owner_userid) {
	return $.ajax({
		type: 'POST',
		url: '/api/v1/cucm/phone/' + device_name,
        data: 
        {
            "description": device_description,
            "device_name": device_name,
            "phonetype": device_model,
            "calleridname": clid_name, 
            "ownerUserName": owner_userid
        }
	});

}

function get_service_status() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/service'
	});
}

function get_device_detail(device_name) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/phone/' + device_name
	});
}

function refresh_perfmon_data() {
    get_perfmon_data().then(function(data) {
        console.log(data['perfmon_counters_result'])

        var calls_active = null
        var calls_completed = null
        var registered_phones = null

        data['perfmon_counters_result'].forEach(function (counter) {
          var counter_name = counter['Name']['_value_1'];
          var counter_value = counter['Value'];

          if (counter_name.includes("CallsActive")) {
            calls_active = counter['Value']
          } else if (counter_name.includes("CallsCompleted")) {
            calls_completed = counter['Value']
          } else if (counter_name.includes("RegisteredHardwarePhones")) {
            registered_phones = counter['Value']
          }
        })
        console.log(calls_active);
        console.log(calls_completed);
        console.log(registered_phones);

        if (calls_active != null) {
          console.log("Updating Calls Active Counter to " + calls_active)
          $("#call_active_counter").html(calls_active);
        }

        if (calls_completed != null) {
          console.log("Updating Calls Completed Counter to " + calls_completed)
          $("#call_completed_counter").html(calls_completed);
        }

        if (registered_phones != null) {
          console.log("Updating Registered Phones Counter to " + registered_phones)
          $("#registered_phones_counter").html(registered_phones);
        }

    });

    get_service_status().then(function(data) {
        var health_text;
        var health_bg; 

        var services_active = 0;
        var services_deactivated = 0; 
        var services_down = 0;

        if (data['service_info']['ReasonCode'] == -1) {
            var service_info_list = data['service_info']['ServiceInfoList']['item'];

            service_info_list.forEach(function(service) {
                service_reason = service['ReasonCode'];
                service_name = service['ServiceName'];
                console.log(service_name + ': ' + service_reason);

                switch (service_reason) {
                    case -1:
                        services_active += 1;
                        break;
                    case -1068:
                        services_deactivated += 1;
                        break; 
                    default:
                        services_down += 1;
                }
            });

            console.log("Service Status: " + 
                        services_active.toString() + " Active, " +
                        services_deactivated.toString() + " Deactivated, " +
                        services_down.toString() + " Down"
                        );

            if (services_down == 0) {
                health_text = "All Services Up";
                health_bg = "success";
            } else {
                health_text = (services_down).toString() + " Down";
                health_bg = "danger";
            }
        } else {
            health_text = "loading...";
            health_bg = "info";
        }

        $("#system_health_text").html(health_text);
        $("#system_health_card").removeClass("bg-info").removeClass("bg-success").removeClass("bg-danger").addClass("bg-" + health_bg);

    });
}

function get_user(username) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/user/' + username
	});
}

function display_user_data(user_data) {
    var name = user_data['firstName'] + ' ' + user_data['lastName'];
    var userid = user_data['userid'];
    var primary_extension = user_data['extensionsInfo']['extension'][0]['pattern']['_value_1'];

    user_data['primary_extension'] = primary_extension;

    var template = `
    <div> 
        <p><strong>Name:</strong> <span id="owner_name">{{firstName}} {{lastName}}</span></p>
        <p><strong>User ID:</strong> <span id="owner_id">{{userid}}</span></p>
        <p><strong>Email Address:</strong> {{mailid}}</p>
        <p><strong>Department:</strong> {{department}}</p>
        <p><strong>Primary Extension:</strong> {{primary_extension}}</p>
        <p><strong>Directory URI:</strong> {{directoryUri}}</p>
        
    </div>
    `;

    var html = Mustache.to_html(template, user_data);

    $('#user_card_title').html('User Details for ' + name + ' (' + userid + ')' );
    $('#user_card_body').html(html);
}

function display_device_table(device_list) {
    console.log(device_list);
    var device_datatable;

    if ( ! $.fn.DataTable.isDataTable( '#device_table' ) ) {
        device_datatable = $('#device_table').DataTable( {
            data: [],
            columns: [
                { title: "Name", width: "170px" },
                { title: "Description" },
                { title: "Model" },
                { title: "Details", width: "25px" },
                { title: "Delete", width: "25px" }
            ]
        });
    } else {
        device_datatable = $('#device_table').DataTable().clear().draw();
    }

    delete_button_html = '<a href="#" class="btn btn-danger btn-circle btn-sm"><i class="fas fa-trash"></i></a>';
    info_button_html = '<a href="#" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';

    device_list.forEach(function(device) {
        get_device_detail(device).then(function(device_details) {
            if (device_details['success'] == true) {
                device_data = device_details['phone_data'];

                device_row = [
                    device_data['name'],
                    device_data['description'],
                    device_data['model'],
                    info_button_html,
                    delete_button_html
                ];     
                device_datatable.row.add(device_row).draw();
            }
        });  
    })
}

function user_search() {
    username = $('#username').val();

    console.log("Searching for " + username);
    if (username !== "") {
        get_user(username).then(function(data) {
            if (data['success'] == true) {
                user_data = data['user_data']
                console.log(user_data);
                display_user_data(user_data);
                display_device_table(user_data['associatedDevices']['device']);
                show_user_fields();
            } else {
                $('#toast-body').html(data['message']);
                $('#status_toast').toast('show');
            }
        });
    }
}

function add_device() {
    device_name = $('#insert_device_name').val();
    device_description = $('#insert_device_description').val();
    device_model = $('#insert_device_model').val();
    clid_name = $('#owner_name').html();
    owner_userid = $('#owner_id').html();

    insert_device(device_name, device_description, device_model, clid_name, owner_userid).then(function(result) {
        console.log(result);
        result['success'] = true;
        if (result['success'] == true) {
            message = "Successfully added " + device_name;
            $("#add_device_status").removeClass('text-danger');
            $("#add_device_status").addClass('text-success');

            delete_button_html = '<a href="#" class="btn btn-danger btn-circle btn-sm"><i class="fas fa-trash"></i></a>';
            info_button_html = '<a href="#" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
            
            device_row = [
                device_name,
                device_description,
                device_model,
                info_button_html,
                delete_button_html
            ];     
            $('#device_table').DataTable().row.add(device_row).draw();
        } else {
            message = "Failed to add " + device_name;
            $("#add_device_status").removeClass('text-success');
            $("#add_device_status").addClass('text-danger');
        }

        $("#add_device_status").html(message);
    });
}

