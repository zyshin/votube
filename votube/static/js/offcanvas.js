$(document).ready(function () {
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });

  var v = $('#video')[0];
  $('track').each(function (index, track) {
    $(track).load(function (e) {
      console.log('track loaded: ' + e.target.label);
      // TODO: lemmatization
      var keyword = $('.word-title').text().trim();
      var re = new RegExp(keyword, 'gi');
      $(e.target.track.cues).each(function (index, cue) {
        cue.text = cue.text.replace(re, '<c.highlighted>$&</c>');
      });
    });
  });
  v.textTracks[0].mode = "showing";
  $('#video').on('pause', function(e) {
    $('#video').addClass('no-sub');
    $('#videoContainer>.video-hover').removeClass('hidden');
    var url = v.currentSrc,
      times = url.substring(url.indexOf('#t=') + 3).split(','),
      start = Number(times[0]);
    v.currentTime = start;
  });
  $('#video').on('play', function(e) {
    $('#video').removeClass('no-sub');
    $('#videoContainer>.video-hover').addClass('hidden');
  });

  $('.btn-play').click(function(e) {
    v.play();
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
