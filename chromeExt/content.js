//////////////// eslext namespace //////////////////////////////////

var eslext = eslext || {};

eslext.dlgName = "extFloatDialog";
eslext.contentName = "extContentIframe";

eslext.dlgDelayTimer = null;

eslext.showDlg =  function(url, e) {
    chrome.runtime.sendMessage({type: "getStatus"}, 
        function(response) {
            if(response.status == 0)
                return;
            $.get(chrome.extension.getURL('/extDialog.html'), function(data) {
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
                content.attr('src', url);
                eslext.dlg = dlg;
            });
        }
    );
};

eslext.hideDlg = function() {
    if(this.dlg)
        this.dlg.remove();
    this.dlg = null;
};

eslext.getSelection = function() {
    var selection;
    if (window.getSelection) {
      selection = window.getSelection();
    } else if (document.selection) {
      selection = document.selection.createRange();
    }
    var s = selection.toString().trim();
    return s;
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
    var s = this.getSelection();
    var parent = this.getSelectionElement();
    if(s !== '' && s.length < 50)  {
        url = 'http://166.111.139.15:9000/?' + 
            'properties=%7B%22ssplit.isOneSentence%22%3A+true%2C+%22' + 
            'outputFormat%22%3A+%22conll%22%2C+%22annotators%22%3A+%22' + 
            'tokenize%2Cssplit%2Cpos%2Clemma%22%2C+%22tokenize.whitespace%22%3A+true%7D';
        $.post(url, s, function(r) {
            // lemma success
            s = r.split('\t')[2];
            // alert(s);
            eslext.showDlg("http://166.111.139.15:8003/votube/?word=" + s + "&plugin=true", e);
        }).fail(function() {
            eslext.showDlg("http://166.111.139.15:8003/votube/?word=" + s + "&plugin=true", e);
        });
    } else
        eslext.hideDlg();
}

//////////////////  namespace ends here //////////////////////////

$(document.body).bind('mouseup', function(e){
    if(eslext.delayTimer) {
        clearTimeout(eslext.delayTimer);
        eslext.delayTimer = null;
    }
    var s = eslext.getSelection();
    if(s !== '' && s.length < 50)
        eslext.delayTimer = setTimeout(function(){eslext.work(e)}, 500);
    else
        eslext.hideDlg();
});