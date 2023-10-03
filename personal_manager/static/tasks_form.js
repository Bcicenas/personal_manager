var selected_tasks = [];

$('input[name="selected_tasks[]"]').each(function(){
	var selected_task_val = $(this).val();
	selected_tasks.push(selected_task_val);

	$('.task-remove-btn').click(function(){ 
		$(this).parent().parent().remove(); 
		selected_tasks.splice(selected_tasks.indexOf(selected_task_val), 1);
	});	
});

$('.task-add-btn').click(function(){
	var selected_task = $('.tasks-dropdown :selected');
	var btn_translation = $('.translation').val()
	if (selected_tasks.indexOf(selected_task.val()) == -1) {
		selected_tasks.push(selected_task.val());
		$('#task_list').append(
			'<tr><td><input type="hidden" name="selected_tasks[]" value="' + selected_task.val() + '" /><a href="/tasks/update/' + selected_task.val() + '">' + selected_task.text() + 
			'</a></td><td class="text-right"><input class="btn btn-danger task-remove-btn" type="button" value="' + btn_translation + '"></td></tr>'
		);

		$('.task-remove-btn').click(function(){ 
			$(this).parent().parent().remove(); 
			var selected_task_val = selected_task.val();
			selected_tasks.splice(selected_tasks.indexOf(selected_task_val), 1);
		});
	}
});
