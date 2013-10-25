<?

/* Database config */
define("DBHOST", "localhost");
define("DBUSER", "domotika");
define("DBPASS", "dmdbpwdmsql");
define("DBNAME", "domotika");

/* API user */
define("APIUSER","admin");
define("APIPASS","domotika");


/* domotikad config */
define("DOMOTIKAD_BASEURI", "https://".APIUSER.":".APIPASS."@127.0.0.1");
define("DOMOTIKAD_BASEPATH", realpath(dirname(__FILE__)."/../../.."));
define("DOMOTIKAD_HTTPPATH", DOMOTIKAD_BASEPATH."/Web/htdocs");
define("DOMOTIKAD_ADMINPATH", DOMOTIKAD_BASEPATH."/Web/admin");

/* Database definitions */
define("DOMODB_WEBSECTION_TABLES", serialize(array("actions",
                                                   "analog",
                                                   "input",
                                                   "output",
                                                   "pwm",
                                                   "video")));


define("DOMODB_DEVSECTION_TABLES", serialize(array("actions",
                                                   "analog",
                                                   "input",
                                                   "output",
                                                   "pwm",
                                                   )));



?>
