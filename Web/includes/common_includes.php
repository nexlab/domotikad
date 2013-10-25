<?
require_once("session.php");
require_once("HTTP/Request.php");
require_once("config.inc.php");
require_once("constants.php");
require_once("meekrodb.php");
require_once("conn.php");
require_once("libraries.php");
require_once("helpers.php");
define("DOMOTIKA", true);
if(startsWith($_SERVER['SCRIPT_FILENAME'], DOMOTIKAD_HTTPPATH)) {
   if(file_exists(DOMOTIKAD_HTTPPATH."includes/common.php"))
      require_once(DOMOTIKAD_HTTPPATH."includes/common.php");
} elseif(startsWith($_SERVER['SCRIPT_FILENAME'], DOMOTIKAD_ADMINPATH)) {
   if(file_exists(DOMOTIKAD_ADMINPATH."includes/common.php"))
      require_once(DOMOTIKAD_ADMINPATH."includes/common.php");
}

?>
