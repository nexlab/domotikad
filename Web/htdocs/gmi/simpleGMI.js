function SimpleGMI(){
    var pagedoc = document;

    //Get top level window's document
    if (top != this)
    {
        pagedoc = parent.document;
    }

    this.refresh = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::refresh";
    }

    this.histroypage = function( times )
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::histroypage::" + times;
    }

    this.historypage = function( times )
    {
            pagedoc.title = "null";
            pagedoc.title = "simpleGMI::histroypage::" + times;
    }

    this.gotoURL = function( url )
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::gotoURL::" + url;
    }

    this.udp = function( host, port, data, udp_cb )
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::udp::" + host + "::" + port + "::" + data + "::" + udp_cb.name;
    }

    this.post = function( url, data, post_cb )
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::post::" + url + "::" + data + "::" + post_cb.name;
    }

    this.hangup = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::hangup";
    }

    this.transfer = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::transfer";
    }

    this.transferTo = function( number)
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::transferTo::" + number;
    }

    this.debug = function( info )
    {
        pagedoc.title = "null";
        pagedoc.title = "-gdebug-" + info;
    }

    this.play = function( url, mode )
    {
        var urls = url.split(";")
        var total_url = "";
        for (var count = 0; count < urls.length; count++)
        {
            if (urls[count].length < 4)
            {
                continue;
            }

            if (urls[count].indexOf("://") != -1)
            {
                final_url = urls[count];
            }
            else
            {
                var temp = this.reverse(location.toString());
                temp = temp.substring(temp.indexOf("/"), temp.length);

                
                final_url = this.reverse(temp) + urls[count];
            }

            total_url += final_url + ";";
        }

        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::play::" + total_url + "::" + mode;
    }

    this.stopPlay = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::stopPlay";
    }

    this.dial = function( account, isVideo, isDialPlan, number, headers )
    {
        pagedoc.title = "null";

        if ( headers != undefined )
        {
            pagedoc.title = "simpleGMI::dial::" + account + "::" + isVideo
                + "::" + isDialPlan + "::" + number + "::" + headers;
        }
        else
        {
            pagedoc.title = "simpleGMI::dial::" + account + "::" + isVideo
                + "::" + isDialPlan + "::" + number;
        }
    }

    this.launchService = function( service, account )
    {
        pagedoc.title = "null";

        if ( account == undefined )
        {
            pagedoc.title = "simpleGMI::launchService::" + service;
        }
        else
        {
            pagedoc.title = "simpleGMI::launchService::" + service + "::" + account;
        }
    }

    this.exit = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::exit";
    }

    this.fullScreen = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::fullScreen";
    }

    this.normalScreen = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "simpleGMI::normalScreen";
    }

    /*Internal use function*/
    this.reverse = function(string)
    {
        var src = "";
        var dst = "";
        src = string;
        while (src.length > 0)
        {
            dst += src.charAt(src.length - 1);
            src = src.substring(0, src.length - 1);
        }
        
        return dst;
    }
}

simpleGMI = new SimpleGMI();
