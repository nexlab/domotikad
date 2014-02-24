$.fn.continouoshold = function(selector, fn, delay, startdelay, first) {

    if (typeof selector === "function") {
        // ( fn, delay, startdelay)
        first = startdelay;
        startdelay = delay;
        delay = fn;
        fn = selector;
        selector = undefined;
    }
    if (typeof delay === "undefined") {
        // (selector, fn) || (fn)
        delay = 100;
    }
    if (typeof startdelay === "undefined") {
        startdelay = 1000;
    }
    if (typeof first === "undefined") {
        first = false;
    }
    if (fn && typeof fn == 'function') {
        var timer = 0, times = 1;
        var clear = function() {
            times = 1;
            clearInterval(timer);
        };
        var initcont = function(evt) {
            var $self = $(this);
            timer = setTimeout(function() {
               $self.trigger("continouoshold");
            }, startdelay);
            if(first)
               fn.call(this, evt);
        };
        this.each(function() {
            $(this).on({
                mousedown: initcont,
                touchstart: initcont,
                continouoshold: function(evt) {
                    var $self = $(this);
                    evt.times = times++;
                    timer = setTimeout(function() {
                        $self.trigger("continouoshold");
                    }, delay);
                    fn.call(this, evt);
                },
                mouseout: clear,
                mouseup: clear,
                mouseleave: clear,
                touchmove: clear,
                touchend: clear
            }, selector);
        });
    }
    return this;
};
