var selected_tasks = [];

$('.task-add-btn').click(function(){
	var selected_task = $('.tasks-dropdown :selected');

	if (selected_tasks.indexOf(selected_task.val()) == -1) {
		selected_tasks.push(selected_task.val());
		$('#task_list').append(
			'<tr><td><input type="hidden" name="selected_tasks[]" value="' + selected_task.val() + '" /><a href="/tasks/update/' + selected_task.val() + '">' + selected_task.text() + 
			'</a></td><td class="text-right"><input class="btn btn-danger task-remove-btn" type="button" value="Remove"></td></tr>'
		);

		$('.task-remove-btn').click(function(){ $(this).parent().parent().remove(); });
	}
});

$('.task-remove-btn').click(function(){ $(this).parent().parent().remove(); });