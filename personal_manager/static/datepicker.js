// prevents html 5 datepicker
$('input[type=date]').on('click', function(event) {
    event.preventDefault();
});

$.fn.datepicker.defaults.format = "yyyy-mm-dd";
$('.datepicker').datepicker({});