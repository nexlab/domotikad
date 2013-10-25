<?
require_once "session.php";
require_once "HTTP/Request.php";
require_once "constants.php";
require_once "config.inc.php";
require_once("meekrodb.php");
require_once("conn.php");


/* OLD FUNCTIONS: deprecated! */
function changeRelay($id=0) //id relay
{
   $req =& new HTTP_Request(DOMOTIKAD_BASEURI."/rest/v1.0/getIOStatus?command=relays_".intval($id));
   if (!PEAR::isError($req->sendRequest())) {
      //$ret=$req->getResponseBody();
      $code = $req->getResponseCode();
      if($code=="302") {
         $req2 =& new HTTP_Request($req->getResponseHeader()["location"]);
         if (!PEAR::isError($req2->sendRequest())) {
            return TRUE;
         }  
         return FALSE;
      }
      return TRUE;
   }
   return FALSE;
}

function wget($url)
{
   $req =& new HTTP_Request($url);
   if (!PEAR::isError($req->sendRequest())) {
      return $req->getResponseBody();
   }
   return '';
}


function getWebSections($excludelist=array("home", "none"), $addlist=array(), $querytype="websection")
{
   if($querytype=="websection")
      $tables=(array)unserialize(DOMODB_WEBSECTION_TABLES);
   else
      $tables=(array)unserialize(DOMODB_DEVSECTION_TABLES);
   $query="";
   foreach($tables as $table)
   {
      if($query!="") $query.=" UNION DISTINCT ";
      $query.="SELECT websection FROM $table";
      foreach($excludelist as $k => $exclude)
      {
         if($k==0) 
            $query.=" WHERE ";
         else
            $query.=" AND ";
         $query.="websection != '$exclude'";
      }
   }
   $query.= " ORDER BY websection";
   $result = DB::queryOneColumn('websection', $query);
   //print_r($query."\n");
   //print_r($result);
   return array_unique(array_merge($result, $addlist));
}

function getDevSections($excludelist=array("home", "none"), $addlist=array())
{
   return getWebSections($excludelist, $addlist, "devsection");
}


function getSectionElements($section, $table='relay', $activeonly=true) {
   $active="";
   switch($table)
   {
      case "relay":
         if($activeonly) $active="AND relay.active=1";
         $query="SELECT relay.*, analog.id AS analogid, input.id AS inputid FROM (relay LEFT JOIN analog ON (analog.ananame=relay.domain AND analog.active=1 $active))  
               LEFT JOIN input ON (input.inpname=relay.domain AND input.active=1) WHERE relay.websection='$section' $active
               ORDER by relay.position,relay.button_name,relay.id";
         break;

      default:
         if($activeonly) $active="AND active=1";
         $query="SELECT * FROM $table WHERE websection='$section' $active ORDER BY button_name";
   }
   return DB::query($query);
} 

?>
