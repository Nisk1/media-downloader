var MessageBox = (function() {
    var $box = null;
    var allowed = { success: true, info: true, warning: true, error: true };

    function init(selector) {
        $box = $(selector);
        $box.hide();
    }

    function _iconFor(type) {
        if (type === 'success') return '✅';
        if (type === 'info') return '❕';
        if (type === 'warning') return '⚠️';
        if (type === 'error') return '❌';
        return '';
    }

    function show(msg, type, autoHide) {
        if (!$box) return;
        type = (typeof type === 'string') ? type.trim() : '';
        if (!allowed[type]) type = 'info';
        var isError = (type === 'error');

        var $text = $box.find('.text');
        if ($text.length) $text.text(msg || 'No message.');

        $box.removeClass('severe showing error success info warning');
        $box.addClass(type === 'error' ? 'severe error' : 'showing ' + type);
        $box.show();

        clearTimeout($box.data('hideTimer'));

        $box.find('#message-close').off('click').on('click', function() {
            clearTimeout($box.data('hideTimer'));
            $box.fadeOut(160).removeClass('showing severe error success info');
        });

        var $icon = $box.find('.icon');
        if ($icon.length) $icon.text(_iconFor(type));

        if (autoHide === false) return;
        var timeout = typeof autoHide === 'number' ? autoHide : (isError ? 7000 : 3500);
        var t = setTimeout(function() {
            $box.fadeOut(250).removeClass('showing severe error success info');
        }, timeout);
        $box.data('hideTimer', t);
    }

    function hide() {
        if (!$box) return;
        clearTimeout($box.data('hideTimer'));
        $box.fadeOut(160).removeClass('showing severe error success info');
    }

    return {
        init: init,
        show: show,
        hide: hide
    };
})();
