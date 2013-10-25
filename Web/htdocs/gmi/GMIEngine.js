function GMI(){
    var pagedoc = document;

    //Get top level window's document
    if (top != this)
    {
        pagedoc = parent.document;
    }

    this.getNetWorkInfo = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "getNetWorkInfo";
    }

    this.getCurrentLanguage = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "getCurrentLanguage";
    }

    this.getCountry = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "getCountry";
    }

    this.getAccountInfo = function()
    {
        pagedoc.title = "null";
        pagedoc.title = "getAccountInfo";
    }

    this.put = function( family, valuelist)
    {
        pagedoc.title = "null";
        pagedoc.title = "put";
    }

    this.get = function( family, keylist)
    {
        pagedoc.title = "null";
        pagedoc.title = "get";
    }
    this.gotoURL = function ( url)
    {
        pagedoc.title = "null";
        pagedoc.title = "gotoURL";
    }
}

GMIEngine = new GMI();
