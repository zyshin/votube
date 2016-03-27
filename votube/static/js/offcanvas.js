$(document).ready(function () {
  $.on = function (event, selector, callback) {
    document.addEventListener(event, function (e) {
      if ($(e.target).is(selector))
        callback(e);
    }, true);
  };

  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });

  $('.row-offcanvas').on('click', '.btn-vote', function (e) {
    var clip_id = $(this).parents('[clip-id]').attr('clip-id'),
      data = {
        'clip_id': clip_id,
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
      };
    console.log('vote-btn clicked: ' + clip_id);
    $('[clip-id="' + clip_id + '"]').find('.btn-vote').addClass('disabled');
    $.post('clip/', data, function (r) {
      if (Number(r) >= 0)
        $('[clip-id="' + clip_id + '"]').find('.num-votes').text(r);
      $('[clip-id="' + clip_id + '"]').find('.btn-vote').removeClass('disabled');
    });
  });

  $.on('play', '#video', function (e) {
    $('#video').removeClass('no-sub');
    $('#videoContainer>.video-hover').addClass('hidden');
  });
  $.on('pause', '#video', function (e) {
    $('#video').addClass('no-sub');
    $('#videoContainer>.video-hover').removeClass('hidden');
  });
  $.on('timeupdate', '#video', function (e) {
    var v = $('#video')[0],
      url = v.currentSrc,
      times = url.substring(url.indexOf('#t=') + 3).split(','),
      start = Number(times[0]),
      end = Number(times[1]);
    if (v.currentTime >= end) {
      v.currentTime = start;
      v.pause();
    }
  });
  $('.row-video').on('click', '.btn-play', function (e) {
    var v = $('#video')[0];
    v.play();
  });
  $.showSubtitle = function (lang) {
    var v = $('#video')[0]
    $(v.textTracks).each(function (index, textTrack) {
      textTrack.mode = 'hidden';
    });
    $(v.textTracks).each(function (index, textTrack) {
      if (textTrack.label == lang) {
        textTrack.mode = 'showing';
        return false;
      }
    });
  };
  $('.row-video').on('click', '.btn-subtitle', function (e) {
    var lang = $(this).hasClass('active') ? 'Eng' : 'Chi-Eng';
    $.showSubtitle(lang);
  });
  $.on('load', 'track', function (e) {
    console.log('track loaded: ' + e.target.label);
    // TODO: lemmatization
    var keyword = $('.word-title').text().trim();
    var re = new RegExp(keyword, 'gi');
    $(e.target.track.cues).each(function (index, cue) {
      cue.text = cue.text.replace(re, '<c.highlighted>$&</c>');
    });
  });

  $('li.list-group-item .btn-clip').click(function (e) {
    var parent = $(this).parents('li.list-group-item'),
      clip_id = parent.attr('clip-id');
    console.log('clip-btn clicked: ' + clip_id);
    if (parent.hasClass('active'))
      return;
    var keyword = $('.word-title').text().trim();
    var data = {
      'word': keyword,
      'clip_id': clip_id
    };
    $('.row-video').load('clip/?' + $.param(data), function (data) {
      // alert('video loaded');
      $('li.list-group-item').removeClass('active');
      parent.addClass('active');
      $.showSubtitle('Eng');
    });
  });
});

(function(b, a) {
  b(function() {
    setTimeout(function() {
      a.setJSReady()
    }, 200);
    var d = !!document.createElement("audio").canPlayType && document.createElement("audio").canPlayType("audio/mpeg") && !b("html").hasClass("ua-linux") && navigator.userAgent.indexOf("Maxthon") < 0;
    var f = "dictVoice.swf?onload=swfLoad&time=" + b.now();
    var c = d ? b('<audio id="dictVoice" style="display: none"></audio>') : b('<object width="1" height= "1" type="application/x-shockwave-flash" id="dictVoice" wmode="transparent" data="' + f + '"><param name="src" value="' + f + '"/><param name="quality" value="high"/><param name="allowScriptAccess" value="always"><param name="wmode" value="transparent" /></object>');
    c.appendTo("body");
    var e = c.get(0);
    c.play = (function() {
      var h = function(k) {
        var j = k;
        if (k.indexOf("http://dict.youdao.com/") < 0) {
          j = "http://dict.youdao.com/dictvoice?audio=" + k
        }
        return j
      };
      var i = function() {
        var j = arguments[0];
        c.attr("src", h(j));
        e.play()
      };
      var g = function() {
        var j = arguments[0];
        stopVoice();
        if (swfReady) {
          b("#simplayer").siblings(".close").click();
          e.playVoice(h(j))
        }
      };
      return (d) ? i : g
    })();
    b("a.voice-js").on("mouseenter", function(g) {
      c.play(b(this).data("rel"));
      g.preventDefault()
    });
    b("a.voice-js,a.humanvoice-js").on("click", function(g) {
      c.play(b(this).data("rel"));
      g.preventDefault()
    });
    window.stopVoice = function() {
      if (b.isFunction(e.stopVoice)) {
        e.stopVoice()
      }
      if (b.isFunction(e.pause)) {
        e.pause();
        if (e.currentTime > 0) {
          e.currentTime = 0
        }
      }
    }
  });
  a.swfReady = false;
  a.jsReady = false;
  a.isContainerReady = function() {
    return jsReady
  };
  a.setSWFIsReady = function() {
    swfReady = true
  };
  a.setJSReady = function() {
    jsReady = true
  }
})(jQuery, window);
