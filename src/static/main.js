$(document).ready(function() {
    ProgressBar.init('#progress-bar', '#progress-container');
    MessageBox.init('#message-box');
    LoadingDots.setElementId('loading-dots');

    var DOWNLOAD_MESSAGES = Array.isArray(window.DOWNLOAD_MESSAGES) && window.DOWNLOAD_MESSAGES.length
        ? window.DOWNLOAD_MESSAGES.slice() : ['🔄 Working... please wait'];

    // Try to replace with JSON from server if available (non-blocking)
    if (typeof window.DOWNLOAD_MESSAGES_URL === 'string' && window.DOWNLOAD_MESSAGES_URL) {
        $.getJSON(window.DOWNLOAD_MESSAGES_URL)
            .done(function(data) {
                if (Array.isArray(data) && data.length) DOWNLOAD_MESSAGES = data;
            })
            .fail(function() {
                // keep whatever DOWNLOAD_MESSAGES already contains
            });
    }

    function pick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    try {
        if (typeof DownloadHandler !== 'undefined' && DownloadHandler && DownloadHandler.init) {
            DownloadHandler.init('#download-btn');
        }
    } catch (e) {
        console.error('DownloadHandler init failed', e);
    }

    $('#download-form').on('submit', function(e) {
        e.preventDefault();

        var formData = $(this).serializeArray();
        var data = {};
        formData.forEach(function(item) { data[item.name] = item.value; });

        $('.message').hide();
        MessageBox.hide();

        $('#message-box').removeData('hideTimer');

        ProgressBar.reset();
        LoadingDots.show();
        $('#url-input').val('');

        if (typeof DownloadHandler !== 'undefined' && DownloadHandler.setDownloading) {
            DownloadHandler.setDownloading(true, data.url);
        }

        $.ajax({
            url: window.location.pathname,
            method: 'POST',
            data: data,
            success: function() {
                var messageInterval = null;

                function startMessageRotation() {
                    if (messageInterval !== null) return;
                    $('#downloading-text').text(pick(DOWNLOAD_MESSAGES)).fadeIn(1000);

                    messageInterval = setInterval(function() {
                        $('#downloading-text').stop(true, true).fadeOut(500, function() {
                            $(this).text(pick(DOWNLOAD_MESSAGES)).fadeIn(500);
                        });
                    }, 5000);
                }
                function stopMessageRotation() {
                    if (messageInterval !== null) {
                        clearInterval(messageInterval);
                        messageInterval = null;
                    }
                }

                var interval = setInterval(function() {
                    $.get("/download-progress/", { key: data.url }, function(resp) {
                        if (resp.progress === null) {
                            ProgressBar.hide();
                            $('#downloading-text').fadeOut(250);
                            LoadingDots.hide();
                            stopMessageRotation();

                            var msgType = (resp.message === "Download cancelled by user!") ? 'warning' : 'error';
                            MessageBox.show(resp.message, msgType, false);

                            clearInterval(interval); // Stop polling
                            if (typeof DownloadHandler !== 'undefined' && DownloadHandler.setDownloading) {
                                DownloadHandler.setDownloading(false);
                            }
                            window.currentDownloadKey = null;
                            return;
                        }

                        ProgressBar.setProgress(resp.progress);

                        if (resp.progress > 0) {
                            ProgressBar.show();
                            startMessageRotation();
                            LoadingDots.hide();
                        } else {
                            ProgressBar.hide();
                        }

                        if (resp.progress >= 100) {
                            ProgressBar.setProgress(100);
                            setTimeout(function() {
                                ProgressBar.hide();
                                $('#downloading-text').fadeOut(500);
                            }, 1500);

                            clearInterval(interval); // Stop polling
                            stopMessageRotation();
                            if (resp.message) {
                                setTimeout(function() {
                                    MessageBox.show(resp.message, "success", false);
                                }, 2000);
                            }
                            if (typeof DownloadHandler !== 'undefined' && DownloadHandler.setDownloading) {
                                DownloadHandler.setDownloading(false);
                            }
                            window.currentDownloadKey = null;
                        }
                    });
                }, 1000); // Check progress every second
            }
        });
    });
});
