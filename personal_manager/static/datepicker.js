// prevents html 5 datepicker
$('input[type=date]').on('click', function(event) {
    event.preventDefault();
});

$('.datepicker').datepicker({
	format: 'yyyy-mm-dd'
});