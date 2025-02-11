function get_ucm_perfmon_data() {
	return $.ajax({
		type: 'POST',
		url: '/api/v1/cucm/perfmon',
        data: JSON.stringify(
        {
            "perfmon_counters": [
                "Cisco CallManager\\RegisteredHardwarePhones",
                "Cisco CallManager\\RegisteredOtherStationDevices",
                "Cisco CallManager\\CallsActive",
                "Cisco CallManager\\CallsCompleted"
            ]
        }),
        contentType: "application/json",
	});
}

function insert_ucm_device(device_name, device_description, device_model, clid_name, owner_userid) {

    param = jQuery.param(
        {
            "description": device_description,
            "device_name": device_name,
            "phonetype": device_model,
            "devicecss": "Unrestricted_CSS",
            "calleridname": clid_name, 
            "ownerUserName": owner_userid
        });

	return $.ajax({
		type: 'POST',
		url: '/api/v1/cucm/phone/' + device_name + '?' + param,
	});
}

function delete_ucm_device(device_name) {
	return $.ajax({
		type: 'DELETE',
		url: '/api/v1/cucm/phone/' + device_name,
	});
}

function get_ucm_service_status() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/service'
	});
}

function get_ucm_device_detail(device_name) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/phone/' + device_name
	});
}

function get_ucm_version() {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/version'
	});
}


function refresh_ucm_perfmon_data() {
    get_ucm_perfmon_data().then(function(data) {
        console.log(data['perfmon_counters_result'])

        var calls_active = null
        var calls_completed = null
        var registered_phones = null
        var registered_softphones = null

        data['perfmon_counters_result'].forEach(function (counter) {
          var counter_name = counter['Name']['_value_1'];
          var counter_value = counter['Value'];

          if (counter_name.includes("CallsActive")) {
            calls_active = counter['Value']
          } else if (counter_name.includes("CallsCompleted")) {
            calls_completed = counter['Value']
          } else if (counter_name.includes("RegisteredHardwarePhones")) {
            registered_phones = counter['Value']
          } else if (counter_name.includes("RegisteredOtherStationDevices")) {
            registered_softphones = counter['Value']
          }
        })
        console.log(calls_active);
        console.log(calls_completed);
        console.log(registered_phones);
        console.log(registered_softphones);

        if (calls_active != null) {
          console.log("Updating Calls Active Counter to " + calls_active)
          $("#call_active_counter").html(calls_active);
        }

        if (calls_completed != null) {
          console.log("Updating Calls Completed Counter to " + calls_completed)
          $("#call_completed_counter").html(calls_completed);
        }

        if (registered_phones != null || registered_softphones != null) {

            if (registered_phones != null) {
                num_registered_phones = parseInt(registered_phones);
            } else {
                num_registered_phones = 0;
            }

            if (registered_softphones != null) {
                num_registered_softphones = parseInt(registered_softphones);
            } else {
                num_registered_softphones = 0;
            }

            var total_registered_phones = (num_registered_phones + num_registered_softphones).toString();

            console.log("Updating Registered Phones Counter to " + total_registered_phones)
            $("#registered_phones_counter").html(total_registered_phones);
        }
  
      });

    get_ucm_service_status(service_status_table).then(function(data) {
        var health_text;
        var health_bg; 

        var services_active = 0;
        var services_deactivated = 0; 
        var services_down = 0;

        var service_list_data = [];

        if (data['service_info']['ReasonCode'] == -1) {
            var service_info_list = data['service_info']['ServiceInfoList']['item'];

            service_info_list.forEach(function(service) {
                service_reason = service['ReasonCode'];
                service_name = service['ServiceName'];
                console.log(service_name + ': ' + service_reason);

                service_list_data.push([
                    service_name, 
                    service['ServiceStatus'], 
                    service['StartTime']
                ]);

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
        
        console.log(service_list_data);
        
        $('#service_status_table').DataTable().clear();
        $('#service_status_table').DataTable().rows.add(service_list_data);
        $('#service_status_table').DataTable().columns.adjust().draw();
        
    });
}

function get_ucm_user(username) {
    return $.ajax({
		type: 'GET',
		url: '/api/v1/cucm/user/' + username
	});
}

function display_ucm_user_data(user_data) {
    var name = user_data['firstName'] + ' ' + user_data['lastName'];
    var userid = user_data['userid'];
    var template = `
    <div> 
        <p><strong>Name:</strong> <span id="owner_name">{{firstName}} {{lastName}}</span></p>
        <p><strong>User ID:</strong> <span id="owner_id">{{userid}}</span></p>
        <p><strong>Email Address:</strong> {{mailid}}</p>
        <p><strong>Department:</strong> {{department}}</p>
        <p><strong>Phone Number:</strong> {{telephoneNumber}}</p>
        <p><strong>Directory URI:</strong> {{directoryUri}}</p>
    </div>
    <div class="container">
       <div class="row">
        <div class="col text-center">
            <a href="#" id="migrate_ucm_to_wbxc_button" class="btn btn-info btn-icon-split">
                <span class="icon text-white-50">
                    <i class="fas fa-arrow-right"></i>
                </span>
                <span class="text">Migrate to Webex Calling</span>
            </a>
        </div>
      </div>
    </div>
    <script>
        $('#migrate_ucm_to_wbxc_button').click(function (e) {
            e.preventDefault();
            migrate_to_wbxc("{{userid}}");
            wait_for_wxc_migration_done(0);
            user_search();
        });
    </script>
    `;

    var html = Mustache.to_html(template, user_data);

    $('#user_card_title').html('User Details for ' + name + ' (' + userid + ')' );
    $('#user_card_body').html(html);
}

function clear_ucm_device_table() {
    if ( $.fn.DataTable.isDataTable( '#device_table' ) ) {
        device_datatable = $('#device_table').DataTable().destroy();
    }
}

function display_ucm_device_table(device_list) {
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

    device_list.forEach(function(device) {
        get_ucm_device_detail(device).then(function(device_details) {
            if (device_details['success'] == true) {
                device_data = device_details['phone_data'];

                device_delete_id = 'device_delete_' + device_data['name'];
                device_info_id = 'device_info_' + device_data['name'];

                delete_button_html = '<a href="#" id="' + device_delete_id + '" class="btn btn-danger btn-circle btn-sm"><i class="fas fa-trash"></i></a>';
                info_button_html = '<a href="#" id="' + device_info_id + '" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                        
                device_row = [
                    device_data['name'],
                    device_data['description'],
                    device_data['model'],
                    info_button_html,
                    delete_button_html
                ];     

                device_datatable.row.add(device_row).draw();
                
                $('#' + device_delete_id).click(function (e) {
                    e.preventDefault();
                    table_row = device_datatable.row( $(this).parents('tr') )
                    var data = table_row.data();
                    console.log(data);
                    device_name = data[0];
                    console.log("Removing " + device_name);
                    remove_ucm_device(device_name, table_row);
                });
    
                $('#' + device_info_id).click(function (e) {
                    e.preventDefault();
                    var data = device_datatable.row( $(this).parents('tr') ).data();
                    console.log(data);
                    device_name = data[0];

                    get_ucm_device_detail(device_name).then(function(device_details) {
                        console.log(device_details);

                        if (device_details['success'] == true) {
                            device_data = device_details['phone_data'];
                            console.log(device_data);
                            device_detail_html = "<pre>" + JSON.stringify(device_data, null, 3) + "</pre>";
                            
                            $('#modal_device_details_title').html("Device Details for <b>"  + device_name + "</b>");
                            $('#modal_device_details').html(device_detail_html);
                            $('#device_modal').modal().show();
                        }

                    });
                });
        
            }
        });  
    })
}

function show_ucm_user_data(user_data) {
    display_ucm_user_data(user_data);
    associated_devices = [];
    if ('associatedDevices' in user_data) {
        if (user_data['associatedDevices'] !== null) {
            try {
                associated_devices = user_data['associatedDevices']['device'];
            } catch (e) {
                console.log(e);
            }
        }
    } 
    display_ucm_device_table(associated_devices);
    check_vm_status();
    check_cms_status();
    show_user_fields();
}

function ucm_user_search() {
    username = $('#username').val();

    console.log("Searching for " + username);
    if (username !== "") {
        get_ucm_user(username).then(function(data) {
            if (data['success'] == true) {
                user_data = data['user_data']
                console.log(user_data);

                show_ucm_user_data(user_data);
            } else {
                $('#toast-body').html(data['message']);
                $('#status_toast').toast('show');
            }
        });
    }
}

function add_ucm_device() {
    device_name = $('#insert_device_name').val();
    device_description = $('#insert_device_description').val();
    device_model = $('#insert_device_model').val();
    clid_name = $('#owner_name').html();
    owner_userid = $('#owner_id').html();

    if (device_name != "") {
        insert_ucm_device(device_name, device_description, device_model, clid_name, owner_userid).then(function(result) {
            console.log("done with insert_ucm_device"); 
            console.log(result);
            if (result['success'] == true) {
                message = "Successfully added " + device_name;
                post_wbxt_notification(message + " for user " + owner_userid);
                $("#add_device_status").removeClass('text-danger');
                $("#add_device_status").addClass('text-success');
    
                device_delete_id = 'device_delete_' + device_name;
                device_info_id = 'device_info_' + device_name;
    
                delete_button_html = '<a href="#" id="' + device_delete_id + '" class="btn btn-danger btn-circle btn-sm"><i class="fas fa-trash"></i></a>';
                info_button_html = '<a href="#" id="' + device_info_id + '" class="btn btn-info btn-circle btn-sm"><i class="fas fa-info-circle"></i></a>';
                        
                device_row = [
                    device_name,
                    device_description,
                    device_model,
                    info_button_html,
                    delete_button_html
                ];     
    
                device_datatable = $('#device_table').DataTable();
                device_datatable.row.add(device_row).draw();
    
                $('#' + device_delete_id).click(function (e) {
                    e.preventDefault();
                    table_row = device_datatable.row( $(this).parents('tr') )
                    var data = table_row.data();
                    console.log(data);
                    device_name = data[0];
                    console.log("Removing " + device_name);
                    remove_ucm_device(device_name, table_row);
                });
        
                $('#' + device_info_id).click(function (e) {
                    e.preventDefault();
                    var data = device_datatable.row( $(this).parents('tr') ).data();
                    console.log(data);
                    device_name = data[0];
    
                    get_ucm_device_detail(device_name).then(function(device_details) {
                        console.log(device_details);
    
                        if (device_details['success'] == true) {
                            device_data = device_details['phone_data'];
                            console.log(device_data);
                            device_detail_html = "<pre>" + JSON.stringify(device_data, null, 3) + "</pre>";
                            
                            $('#modal_device_details_title').html("Device Details for <b>"  + device_name + "</b>");
                            $('#modal_device_details').html(device_detail_html);
                            $('#device_modal').modal().show();
                        }
    
                    });
                });
    
            } else {
                message = "Failed to add " + device_name;
                post_wbxt_notification(message + " for user" + owner_userid);
                $("#add_device_status").removeClass('text-success');
                $("#add_device_status").addClass('text-danger');
            }
    
            $("#add_device_status").html(message);
        });
    } else {
        $("#add_device_status").html("Device Name must not be blank.");
        $("#add_device_status").removeClass('text-success');
        $("#add_device_status").addClass('text-danger');
    }


}

function remove_ucm_device(device_name, table_row) {
    delete_ucm_device(device_name).then(function(result) {
        if (result['success'] == true) {
            table_row.remove().draw();
            post_wbxt_notification("Successfully Deleted Device " + device_name);
        } else {
            console.log(result);
        }
    });
}

function update_ucm_version() {
    get_ucm_version().then(function(result) {
        console.log(result);
        if (result['success'] == true) {
            version = result['version'];
        } else {
            version = "unknown";
        }

        $('#ucm_version').html(version);
    });
}

function migrate_to_wbxc(username) {
    console.log("migrate_to_wbxc for " + username);
    return $.ajax({
		type: 'PUT',
		url: '/api/v1/core/migrate_cloud/' + username
	});
}