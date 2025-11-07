(function(global, $) {
    'use strict';

    var DownloadHandler = (function() {
    var isDownloading = false;
    var $button = null;
    var originalHtml = '';
    var originalDisabled = false;
    var cancelClickNamespace = '.downloadCancel';
    var currentKey = null;

    function sendCancelRequest(key, cb) {
        if (!key) { cb && cb(false); return; }
            fetch('/stop-download/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: key })
        }).then(function(resp){ return resp.json(); })
            .then(function(json) { cb && cb(!!json.success); })
            .catch(function() { cb && cb(false); });
    }

    function setButtonToCancel() {
        if (!$button) return;
        $button.data('wasDisabled', originalDisabled);
        $button.prop('disabled', false);
        $button.addClass('cancelling');
        $button.html('Cancel ❌');
    
        $button.off(cancelClickNamespace).on('click' + cancelClickNamespace, function(e) {
        e.preventDefault();
        if (!isDownloading) return;
        $button.prop('disabled', true);
        sendCancelRequest(currentKey, function(success) {
            if (!success) {
                if (typeof global.showMessage === 'function') {
                  global.showMessage('Could not cancel download', 'warning');
                } else if (window.$) {
                  $('#message-box .text').text('Could not cancel download');
                }
                $button.prop('disabled', false);
            }
        });
      });
    }

    function restoreDownloadButton() {
        if (!$button) return;
        $button.off(cancelClickNamespace);
        $button.removeClass('cancelling');
        $button.prop('disabled', false);
        $button.html(originalHtml);
    }

    return {
        init: function(buttonSelector) {
            $button = (buttonSelector instanceof $) ? buttonSelector : $(buttonSelector || '#download-btn');
            if (!$button || !$button.length) {
              throw new Error('DownloadHandler: button not found: ' + buttonSelector);
            }
            originalHtml = $button.html();
            originalDisabled = $button.prop('disabled');
        },

        setDownloading: function(active, key) {
            isDownloading = !!active;
            currentKey = key || null;
            if (isDownloading) {
              setButtonToCancel();
            } else {
              restoreDownloadButton();
            }
        },

        restore: function() {
            isDownloading = false;
            currentKey = null;
            restoreDownloadButton();
        },

        isDownloading: function() { return isDownloading; },
        currentKey: function() { return currentKey; },
    
        _sendCancelRequest: sendCancelRequest
    };
  }());

    global.DownloadHandler = DownloadHandler;
})(window, window.jQuery);
