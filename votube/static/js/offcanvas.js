$(document).ready(function () {
  $.on = function (event, selector, callback) {
    document.addEventListener(event, function (e) {
      if ($(e.target).is(selector))
        callback(e);
    }, true);
  };

  $.deparam = function (querystring) {
      // remove any preceding url and split
      querystring = querystring.substring(querystring.indexOf('?')+1).split('&');
      var params = {}, pair, d = decodeURIComponent, i;
      // march and parse
      for (i = querystring.length; i > 0;) {
          pair = querystring[--i].split('=');
          params[d(pair[0])] = d(pair[1]);
      }
      return params;
  };

  $.getParams = function(clip, movie, sense) {
    var url = window.location.href,
      params = $.deparam(url.substring(url.indexOf('?') + 1));
    return {
      'word': $('.word-title').text().trim(),
      'clip_id': (clip || $('.video-controls')).attr('clip-id'),
      'movie_id': (movie || $('.dropdown-menu>li.active')).attr('movie-id'),
      'sense_id': (sense || $('.pager>li.current')).attr('sense-id'),
      'sessionid': $('input[name="sessionid"]').val(),
      'pid': params.pid,
      'context': params.context
    };
    // TODO: if ($.isPlugin) add plugin to params
  }

  $.stopLoading = function() {
    if(window.stop !== undefined) {
      window.stop();
    } else if(document.execCommand !== undefined) {
      document.execCommand("Stop", false);
    }
  }

  $.isPlugin = ($('.plugin').length > 0);

  // $.waitTime = 300;
  $.autoPlay = false;

  $('.navbar-form').submit(function () {
    $('.input-search').val($('.input-search').val() || $('.input-search').attr('placeholder'));
  });

  $('[data-toggle="tooltip"]').tooltip({ html: true });
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });

  $('.row-offcanvas').on('click', '.btn-vote', function (e) {
    var data = $.getParams(),
      clip_id = $(this).parents('[clip-id]').attr('clip-id');
    data.clip_id = clip_id;
    data.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
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
    $('.sense-text').removeClass('hidden');
    var data = $.getParams();
    data.lang = $('.btn-subtitle').hasClass('active') ? 'DUAL' : 'EN';
    $.get('view/', data);
  });
  $.on('pause', '#video', function (e) {
    $('#video').addClass('no-sub');
    $('#videoContainer>.video-hover').removeClass('hidden');
    // window.stop();
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
    if (v.readyState == 4) {
      v.play();
    }
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
    $('.full-sent-chinese').toggleClass('hidden');
    $.showSubtitle(lang);
    // $('.btn-play').click();
    var data = $.getParams();
    data.lang = (lang == 'Eng') ? 'EN' : 'DUAL';
    $.get('subtitle/', data);
  });
  $.on('load', 'track', function (e) {
    var track = e.target;
    console.log('track loaded: ' + track.label);
    var highlights = $('.full-sent em').map(function(i, o) { return $(o).text() });
    $(track.track.cues).each(function (index, cue) {
      $(highlights).each(function(i, h) {
        cue.text = cue.text.replace(h, '<c.highlighted>$&</c>')
      });
    });
    if (track.label == 'Chi-Eng') {
      var bilingual = $('.full-sent-chinese').html() + '\n' + $('.full-sent').html()
      alignToolkit.alignEm(bilingual, function(str) {
        if (str) {
          var ch = str.split('\n')[0];
          $('.full-sent-chinese').html(ch);
          var highlights = $('.full-sent-chinese em.em1').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted1>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em2').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted2>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em3').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted3>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em4').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted4>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em5').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted5>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em6').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted6>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em7').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted7>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em8').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted8>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em9').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted9>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em10').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted10>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em11').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted11>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em12').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted12>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em13').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted13>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em14').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted14>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em15').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted15>$&</c>')
            });
          });
          highlights = $('.full-sent-chinese em.em16').map(function(i, o) { return $(o).text() });
          $(track.track.cues).each(function (index, cue) {
            $(highlights).each(function(i, h) {
              cue.text = cue.text.replace(h, '<c.highlighted16>$&</c>')
            });
          });
          ch = ch.replace(/<em class='em1'>/g,'<b><font color=#ffce3f>');
          ch = ch.replace(/<\/em>/g,'</font></b>')
          ch = ch.replace(/<em class='em2'>/g,'<b><font color=#ffd14c>');
          ch = ch.replace(/<em class='em3'>/g,'<b><font color=#ffd559>');
          ch = ch.replace(/<em class='em4'>/g,'<b><font color=#ffd865>');
          ch = ch.replace(/<em class='em5'>/g,'<b><font color=#ffdb72>');
          ch = ch.replace(/<em class='em6'>/g,'<b><font color=#ffde7f>');
          ch = ch.replace(/<em class='em7'>/g,'<b><font color=#ffe28c>');
          ch = ch.replace(/<em class='em8'>/g,'<b><font color=#ffe599>');
          ch = ch.replace(/<em class='em9'>/g,'<b><font color=#ffe8a5>');
          ch = ch.replace(/<em class='em10'>/g,'<b><font color=#ffebb2>');
          ch = ch.replace(/<em class='em11'>/g,'<b><font color=#ffefbf>');
          ch = ch.replace(/<em class='em12'>/g,'<b><font color=#fff2cc>');
          ch = ch.replace(/<em class='em13'>/g,'<b><font color=#fff5d9>');
          ch = ch.replace(/<em class='em14'>/g,'<b><font color=#fff8e5>');
          ch = ch.replace(/<em class='em15'>/g,'<b><font color=#fffcf2>');
          ch = ch.replace(/<em class='em16'>/g,'<b><font color=#ffffff>');
          console.log(ch);
          $('.full-sent-chinese').html(ch);
        }
      });
    }
  });
  if ($('#video').attr('src')) {
    if (!$.isPlugin) {
      $('.sense-text').addClass('hidden');
    }
    $('.row-video').addClass('loading');
    $.time = Date.now();
  }
  $.on('loadstart', '#video', function (e) {
    if (!$.isPlugin) {
      $('.sense-text').addClass('hidden');
    }
    $('.row-video').addClass('loading');
    $.time = Date.now();
  });
  $.on('loadeddata', '#video', function (e) {
    $('.row-video').removeClass('loading');
    $.showSubtitle('Chi-Eng');
    $.showSubtitle('Eng');
    if ($.autoPlay) {
      // setTimeout(function () {
        $('.btn-play').click();
      // }, $.waitTime);
    }
    if (!$.isPlugin) {
      $.autoPlay = true;
    }
    var data = $.getParams();
    data.loadTime = Date.now() - $.time;
    $.get('loadtime/', data);
  });

  $('#sidebar').on('click', '.btn-clip', function (e) {
    var parent = $(this).parents('[clip-id]');
    console.log('clip-btn clicked: ' + parent.attr('clip-id'));
    if (parent.hasClass('active'))
      return;
    var data = $.getParams(parent, null, null);
    $('.row-video').load('clip/?' + $.param(data), function (r) {
      $('li.list-group-item').removeClass('active');
      parent.addClass('active');
      $('[data-toggle="tooltip"]').tooltip({ html: true });
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
