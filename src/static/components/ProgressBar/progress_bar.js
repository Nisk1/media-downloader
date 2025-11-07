var ProgressBar = (function() {
    var $bar = null;
    var $container = null;

    function init(barSelector, containerSelector) {
        $bar = $(barSelector);
        $container = $(containerSelector);
        reset();
    }

    function reset() {
        if (!$bar) return;
        $bar.removeClass('complete').css('width', '0%').text('0%').hide();
        if ($container) $container.hide();
    }

    function show() {
        if (!$bar || !$container) return;
        $container.fadeIn(500);
        $bar.fadeIn(500);
    }

    function hide() {
        if (!$bar || !$container) return;
        $container.fadeOut(500);
        $bar.fadeOut(250);
    }

    function setProgress(percent) {
        if (!$bar) return;
        var text = (typeof percent === 'number') ? Math.max(0, Math.min(100, Math.round(percent))) + '%' : percent;
        $bar.css('width', text).text(text);
        if (typeof percent === 'number' && percent >= 100) {
            $bar.addClass('complete').css('width', '100%').text('100%');
        } else {
            $bar.removeClass('complete');
        }
    }

    return {
        init: init,
        reset: reset,
        show: show,
        hide: hide,
        setProgress: setProgress
    };
})();
