function post_wbxt_notification(message) {
    return $.ajax({
		type: 'POST',
        url: '/api/v1/wbxt/send_message',
        data: {
            'room_name': 'HOLCOL-2574 Notifications',
            'text': message
        }
	});
}