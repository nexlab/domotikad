/* Fastclick Hammer + jquery */
jQuery.fn.fastClick = function(handler) {
        this.click(function(ev) { ev.preventDefault(); });
        Hammer(this[0]).on("tap doubletap", handler);
        return this;
    };
/* end fastclick */

