$.fn.mousehold = function(selector, fn, delay) {
    if (typeof selector === "function") {
        // ( fn, delay )
        delay = fn;
        fn = selector;
        selector = undefined;
    }
    if (typeof delay === "undefined") {
        // (selector, fn) || (fn)
        delay = 100;
    }
    if (fn && typeof fn == 'function') {
        var timer = 0, times = 1;
        var clear = function() {
            times = 1;
            clearInterval(timer);
        };
        this.each(function() {
            $(this).on({
                mousedown: function(evt) {
                    var $self = $(this);
                    evt.times = times++;
                    timer = setTimeout(function() {
                        $self.trigger("mousedown");
                    }, delay);
                    fn.call(this, evt);
                },
                mouseout: clear,
                mouseup: clear
            }, selector);
        });
    }
    return this;
};
