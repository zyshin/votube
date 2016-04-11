//////////////// eslext namespace //////////////////////////////////

var eslext = eslext || {};

eslext.dlgName = "extFloatDialog";
eslext.contentName = "extContentIframe";

eslext.dlgDelayTimer = null;

eslext.jumpTarget = "";

eslext.showDlg =  function(sel, e) {
    $.get(chrome.extension.getURL('/extDialog.html'), function(data) {
        var word = sel.s;
        $(data).appendTo('body');
        offset = 10;
        eslext.hideDlg();
        dlg = $('#' + eslext.dlgName);
        w = parseInt(dlg.css("width"));
        h = parseInt(dlg.css("height"));
        W = window.innerWidth;
        H = window.innerHeight;
        x = e.pageX + offset;
        y = e.pageY + offset;
        if(e.clientX > W - w)
            x -= w + offset * 2;
        if(e.clientY > H - h)
            y -= h + offset * 2;
        dlg.css("top", y);
        dlg.css("left", x);
        dlg.css("display", "block");
        content = $('#' + eslext.contentName);
        var url = "http://166.111.139.15:8003/votube/?word=" + word + "&plugin=true&context=" + sel.context;
        content.attr('src', url);
        url = "http://166.111.139.15:8003/votube/?word=" + word;
        eslext.jumpTarget = url;
        //$("#extControlLink").attr('href', url);
        $("#extControlImage").attr('src', chrome.extension.getURL('play.png'));
        $("#extControlImage").attr('onclick', "window.location.href = '" + url + "'");
        eslext.dlg = dlg;
    });
};

eslext.doJump = function() {
}

eslext.hideDlg = function() {
    if(this.dlg)
        this.dlg.remove();
    this.dlg = null;
};

eslext.getSelection = function() {
    var ret = {};
    var selection;
    if (window.getSelection) {
        selection = window.getSelection();
        ret.s = selection.toString().trim();
        if(ret.s.length == 0)
            return ret;
        ret.pos = selection.getRangeAt(0);
        var value = ret.pos.startContainer.nodeValue;
        var pre = "";
        var post = "";
        for(var i = ret.pos.startOffset - 1; i >= 0 && (value[i] == ' ' || ret.pos.startOffset - i < 500) && ".!?".indexOf(value[i]) === -1; --i)
            pre = value[i] + pre;
        for(var i = ret.pos.endOffset; i < value.length && (value[i] == ' ' || i - ret.pos.endOffset < 500) && ".!?".indexOf(value[i]) === -1; ++i) 
            post = post + value[i];
        ret.context = pre + "<em>" + value.substring(ret.pos.startOffset, ret.pos.endOffset) + "</em>" + post + ".";
        console.log(ret.context);
    }
    return ret;
}

eslext.getSelectionElement = function getSelectedNode()
{
    var ret = null;
    if (document.selection)
        ret = document.selection.createRange().parentElement();
    else
    {
        var selection = window.getSelection();
        if (selection.rangeCount > 0)
            ret = selection.getRangeAt(0).startContainer.parentNode;
    }
    if(ret) {
        ret = $(ret);
        return ret.html();
    }
    return "";
}

eslext.work = function (e) {
    var sel = this.getSelection();
    var s = sel.s;
    if(s !== '' && s.length < 50)  {
        url = 'http://166.111.139.15:9000/?' + 
            'properties=%7B%22ssplit.isOneSentence%22%3A+true%2C+%22' + 
            'outputFormat%22%3A+%22conll%22%2C+%22annotators%22%3A+%22' + 
            'tokenize%2Cssplit%2Cpos%2Clemma%22%2C+%22tokenize.whitespace%22%3A+true%7D';
        chrome.runtime.sendMessage({type: "getStatus"}, 
            function(response) {
                if(response.status == 0)
                    return;
                $.post(url, s, function(r) {
                    // lemma success
                    sel.s = r.split('\t')[2];
                    // alert(s);
                    eslext.showDlg(sel, e);
                }).fail(function() {
                    eslext.showDlg(sel, e);
                });
            }
        );
    } else
        eslext.hideDlg();
}

//////////////////  namespace ends here //////////////////////////

$(document.body).bind('mouseup', function(e){
    if(eslext.delayTimer) {
        clearTimeout(eslext.delayTimer);
        eslext.delayTimer = null;
    }
    var sel = eslext.getSelection();
    var s = sel.s;
    if(s !== '' && s.length < 50)
        eslext.delayTimer = setTimeout(function(){eslext.work(e)}, 500);
    else
        eslext.hideDlg();
});
