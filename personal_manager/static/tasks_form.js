var selected_tasks = [];

$('input[name="selected_tasks[][\'task_id\']"]').each(function(){
	var selected_task_val = $(this).val();
	selected_tasks.push(selected_task_val);

	$('.task-remove-btn').click(function(){ 
		$(this).parent().parent().remove(); 
		selected_tasks.splice(selected_tasks.indexOf(selected_task_val), 1);
	});	
});

$('.task-add-btn').click(function(){
	var selected_task = $('.tasks-dropdown :selected');
	var selected_start_time = $('.start-time-dropdown :selected');
	var btn_translation = $('.translation').val()
	if (selected_tasks.indexOf(selected_task.val()) == -1) {
		selected_tasks.push(selected_task.val());
		$('#task_list').append(
			'<tr><td><input type="hidden" name="selected_tasks[][\'task_id\']" value="' + selected_task.val() + '" /><a href="/tasks/update/' + selected_task.val() + '">' + selected_task.text() + 
			'<td><input type="hidden" name="selected_tasks[][\'start_time\']" value="' + selected_start_time.val() + '" />' + selected_start_time.text() +' h</td><td class="selected-duration-' + selected_task.val() + '"></td>'+
			'</a></td><td class="text-right"><input class="btn btn-danger task-remove-btn" type="button" value="' + btn_translation + '"></td></tr>'
		);

		getTaskDuration(selected_task.val());
		$('.task-remove-btn').click(function(){ 
			$(this).parent().parent().remove(); 
			var selected_task_val = selected_task.val();
			selected_tasks.splice(selected_tasks.indexOf(selected_task_val), 1);
		});
	}
});


function getTaskDuration(task_id){
  var result = '0.0 h'
  $.get("/tasks/get_task_duration/" + task_id, function(data, status){
  	result = parseInt(data) / 60;
  	$('.selected-duration-' + task_id).text(result + ' h');
  });
}
