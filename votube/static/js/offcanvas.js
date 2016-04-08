$(document).ready(function () {
  $.on = function (event, selector, callback) {
    document.addEventListener(event, function (e) {
      if ($(e.target).is(selector))
        callback(e);
    }, true);
  };

  $.getParams = function(clip, movie, sense) {
    return {
      'word': $('.word-title').text().trim(),
      'clip_id': (clip || $('.video-controls')).attr('clip-id'),
      'movie_id': (movie || $('.dropdown-menu>li.active')).attr('movie-id'),
      'sense_id': (sense || $('.pager>li.current')).attr('sense-id'),
      'sessionid': $('input[name="sessionid"]').val()
    };
  }

  $.stopLoading = function() {
    if(window.stop !== undefined) {
      window.stop();
    } else if(document.execCommand !== undefined) {
      document.execCommand("Stop", false);
    }
  }

  $.waitTime = 2000;

  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });

  $('.row-offcanvas').on('click', '.btn-vote', function (e) {
    var clip_id = $(this).parents('[clip-id]').attr('clip-id'),
      data = {
        'clip_id': clip_id,
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
        'sessionid': $('input[name="sessionid"]').val()
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
    $('.fa-spin').addClass('hidden');
    var data = $.getParams();
    data.lang = $('.btn-subtitle').hasClass('active') ? 'DUAL' : 'EN';
    $.get('view/', data);
  });
  $.on('pause', '#video', function (e) {
    $('#video').addClass('no-sub');
    $('#videoContainer>.video-hover').removeClass('hidden');
    window.stop();
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
  $('.row-video').on('click', '#video', function (e) {
    var v = $('#video')[0];
    v.pause();
  });
  $('.row-video').on('click', '.video-hover', function (e) {
    $('.btn-play').click()
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
    $('.btn-play').click();
  });
  $.on('load', 'track', function (e) {
    console.log('track loaded: ' + e.target.label);
    var keyword = $('.word-title').text().trim(),
      morph = $('[morph]').attr('morph'),
      re = new RegExp(keyword, 'gi'),
      re2 = new RegExp(morph, 'gi');
    $(e.target.track.cues).each(function (index, cue) {
      cue.text = cue.text.replace((cue.text.match(re2)) ? re2 : re, '<c.highlighted>$&</c>');
      if (e.target.label == 'Chi-Eng') {
        // convert to Simplified Chinese
        cue.text = alignToolkit.chnConv(cue.text);
        // highlight Chinese keywords according to <c.highlighted>English</c>
        if (cue.text.indexOf('</c>') >= 0) {
          alignToolkit.alignEm(cue.text, function(str) {
            if(str != null)
              cue.text = str;
          }, 'simp');
        }
      }
    });
  });
  $.on('loadeddata', '#video', function (e) {
    $('.fa-spin').removeClass('hidden');
    $.showSubtitle('Chi-Eng');
    $.showSubtitle('Eng');
    setTimeout(function () {
      $.waitTime = 300;
      $('.btn-play').click();
    }, $.waitTime);
  });

  $('#sidebar').on('click', '.btn-clip', function (e) {
    var parent = $(this).parents('li.list-group-item');
    console.log('clip-btn clicked: ' + parent.attr('clip-id'));
    if (parent.hasClass('active'))
      return;
    var data = $.getParams(parent, null, null);
    $('.row-video').load('clip/?' + $.param(data), function (r) {
      $('li.list-group-item').removeClass('active');
      parent.addClass('active');
    });
  });
  $('#sidebar').on('click', '.btn-movie', function (e) {
    var parent = $(this).parents('li');
    console.log('movie-btn clicked: ' + parent.attr('movie-id'));
    if (parent.hasClass('active'))
      return;
    var data = $.getParams(null, parent, null);
    $('#sidebar').load('movie/?' + $.param(data));
  });
  $('#sidebar').on('click', '.btn-sense', function (e) {
    var parent = $(this).parents('li');
    console.log('sense-btn clicked: ' + parent.attr('sense-id'));
    var data = $.getParams(null, null, parent);
    $('#sidebar').load('movie/?' + $.param(data));
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
