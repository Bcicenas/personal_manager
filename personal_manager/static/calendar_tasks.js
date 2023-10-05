$('.calendar-day').click(function(){
	$('.calendar-day').removeClass('selected-day');
	$(this).addClass('selected-day');
	$('.calendar-day-card').hide();
	$('#calendar_day' + $(this).find('.c-day').text()).show();
})