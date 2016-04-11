$(document).ready(function () {
  $.waitTime = 2000;
  $.waitTime2 = 300;

  $('.row-video').on('click', '.btn-clip-next', function (e) {
    e.stopPropagation();
    console.log('clip-btn-next clicked: ' + $(this).attr('clip-id'));
    var data = $.getParams($(this), null, $(this));
    data.plugin = true;
    $('.row-video').load('clip/?' + $.param(data), function (r) {
      $('[data-toggle="tooltip"]').tooltip({ html: true });
    });
  });
});
