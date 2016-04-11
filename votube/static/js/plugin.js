$(document).ready(function () {
  $.waitTime = 3000;
  $.waitTime2 = 3000;

  $('.row-video').on('click', '.btn-clip-next', function (e) {
    console.log('clip-btn-next clicked: ' + $(this).attr('clip-id'));
    var data = $.getParams($(this), null, null);
    $('.row-video').load('clip/?' + $.param(data), function (r) {
      $('[data-toggle="tooltip"]').tooltip({ html: true });
    });
  });
});
