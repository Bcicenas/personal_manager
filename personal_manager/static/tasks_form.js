var selected_tasks = [];

$('input[name="selected_tasks[][\'task_id\']"]').each(function(index){
	var selected_task_val = $(this).val();
	selected_tasks.push(selected_task_val);
	getTaskDuration(selected_task_val, $('input[name="selected_tasks[][\'start_time\']"]')[index].value, false);

	$('#task_remove' + selected_task_val).click(function(){
		getTaskDuration(selected_task_val, $('input[name="selected_tasks[][\'start_time\']"]')[selected_tasks.indexOf(selected_task_val)].value, false, false);  
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
			'</a></td><td class="text-right"><input class="btn btn-danger task-remove-btn" id="task_remove' + selected_task.val() + '" type="button" value="' + btn_translation + '"></td></tr>'
		);

		getTaskDuration(selected_task.val(), selected_start_time.val());
		$('#task_remove' + selected_task.val()).click(function(){
			getTaskDuration(selected_task.val(), selected_start_time.val(), false, false); 
			$(this).parent().parent().remove(); 
			var selected_task_val = selected_task.val();
			// updateStartTimeDropdown(selected_start_time.val());
			selected_tasks.splice(selected_tasks.indexOf(selected_task_val), 1);
		});
	}
});


function getTaskDuration(task_id, start_time, update_duration_column = true, disabled = true){
  var result = '0.0 h'
  $.get("/tasks/get_task_duration/" + task_id, function(data, status){
  	result = parseInt(data) / 60;
  	updateStartTimeDropdown(start_time, result, disabled);
  	if(update_duration_column) $('.selected-duration-' + task_id).text(result + ' h');
  });
}

function updateStartTimeDropdown(start_time, duration, disabled = true){
	for(var index = start_time; index < Math.ceil(parseInt(start_time) + duration); index++){
		$('.start-time-dropdown>option')[index].disabled = disabled;
	}
	checkStartTimeStatus();
}

$('.start-time-dropdown').change(function(){
	checkStartTimeStatus();
});

function checkStartTimeStatus(){
	if($('.start-time-dropdown :selected').is(':disabled')){
		$('.task-add-btn').attr('disabled', true);
	}else{
		$('.task-add-btn').attr('disabled', false);
	}	
}