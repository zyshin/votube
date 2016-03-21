
function setIcon() {
	chrome.browserAction.setIcon({
		path: (localStorage.status == 1) ? "icons/icon_1.png" : "icons/icon_0.png"});	
}

chrome.browserAction.onClicked.addListener(function(tab) {
	if(!localStorage.status)
		localStorage['status'] = 1;
	localStorage['status'] = 1 - parseInt(localStorage['status']);
	setIcon();
});

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.type == "getStatus")
    	sendResponse({status: localStorage.status});
});

setIcon();