var LoadingDots = (function() {
    var elId = 'loading-dots';

    function show() {
        var el = document.getElementById(elId);
        if (!el) return;
        el.style.display = 'flex';
    }

    function hide() {
        var el = document.getElementById(elId);
        if (!el) return;
        el.style.display = 'none';
    }

    function setElementId(id) {
        if (typeof id === 'string') elId = id;
    }

    return {
        show: show,
        hide: hide,
        setElementId: setElementId
    };
})();
