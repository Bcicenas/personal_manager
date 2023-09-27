var selected_tasks = [];

$('.task-add-btn').click(function(){
	var selected_task = $('.tasks-dropdown :selected');

	if (selected_tasks.indexOf(selected_task.val()) == -1) {
		selected_tasks.push(selected_task.val());
		$('#task_list').append(
			'<p><input type="hidden" name="selected_tasks[]" value="' + selected_task.val() + '" />' + selected_task.text() + 
			'<input class="btn btn-danger task-remove-btn" type="button" value="Remove"></p>'
		);

		$('.task-remove-btn').click(function(){ $(this).parent().html(''); });
	}
});

$('.task-remove-btn').click(function(){ $(this).parent().html(''); });