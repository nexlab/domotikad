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

/* NEW FUNCTIONS */

function getPanelIO($table, $content, $websection, $activeonly=true, $where="",$orderby="", $limit="")
{
   if($table=='input')
   {
      $dom="inpname";
      $ljoin="inpstatus on input.id=inpstatus.buttonid";
      $add="inpstatus.status as status";
   }
   elseif($table=='analog')
   {
      $dom="ananame";
      $ljoin="anastatus on analog.id=anastatus.buttonid";
      $add="anastatus.status as status";
   }
   elseif($table=="relay")
   {
      $add="relstatus.status as status,relstatus.ampere as ampere";
      $dom="domain";
      $ljoin="relstatus on relay.id=relstatus.buttonid";
   }
   elseif($table=='actions')
   {
      $dom="ikap_dst";
      $ljoin="actstatus on actions.id=actstatus.buttonid";
      $add="actstatus.status as status, actstatus.status2 as status2";
   }
   else // output 
   {
      $add="";
      $ljoin="";
      $dom="domain";
   }
   $sqlquery="SELECT $table.*,'$table' as devtype";
   if($add!="")
      $sqlquery.=",$add";
   $sqlquery.=" FROM $table";
   if($ljoin!="")
      $sqlquery.=" LEFT JOIN ".$ljoin;
   if($websection!="*" || $content!="" || $activeonly || $where)
      $sqlquery.=" WHERE";
   if($websection!="*")
   {
      $wbss=explode(',',str_replace('DMDOMAIN:','',$websection));
      if(count($wbss)>1)
      {
      }
      if(startsWith($websection, 'DMDOMAIN:'))
      {
         if(count($wbss)>1)
         {
            $sqlquery.=" (";
            $wbstart=TRUE;
            foreach($wbss as $wbs)
            {
               if($wbstart==TRUE)
                  $wbstart=FALSE;
               else
                  $sqlquery.=" OR ";
               $sqlquery.=" DMDOMAIN(websection, '".$wbs."')=1";
            }
            $sqlquery.=" )";
         }
         else
            $sqlquery.=" DMDOMAIN(websection, '".str_replace('DMDOMAIN:','',$websection)."')=1";
      }
      else
      {
         if(count($wbss)>1)
         {
            $sqlquery.=" websection IN (";
            $wbstart=TRUE;
            foreach($wbss as $wbs)
            {
               if($wbstart==TRUE)
                  $wbstart=FALSE;
               else
                  $sqlquery.=",";
               $sqlquery.="'".$wbs."'";
            }
            $sqlquery.=")";
         }
         else
            $sqlquery.=" websection='".$websection."'";
      }
   }
   if($websection!="*" && $activeonly)
      $sqlquery.=" AND";
   if($activeonly)
      $sqlquery.=" active>0";
   if(($websection!="*" || $activeonly) && $content!="")
      $sqlquery.=" AND";
   if($content!="")
   {
      $dmds=explode(',',$content);
      if(count($dmds)<2)
         $sqlquery.=" DMDOMAIN($table.$dom, '".$content."')=1";
      else
      {
         $sqlquery.=" (";
         $dmstart=TRUE;
         foreach($dmds as $dmd)
         {
            if($dmstart==TRUE)
               $dmstart=FALSE;
            else
               $sqlquery.=" OR ";
            $sqlquery.=" DMDOMAIN($table.$dom, '".$dmd."')=1";

         }
         $sqlquery.=" )";
      }
   }
   if(($websection!="*" || $activeonly || $content!="") && $where!="")
      $sqlquery.=" AND";
   if($where!="")
      $sqlquery.=" ".$where;
   if($orderby=="")
      $sqlquery.=" ORDER by position,button_name ASC";
   else
      $sqlquery.=" ORDER by $orderby";
   if($limit!="")
       $sqlquery.=" LIMIT ".intval($limit);
   //print_r($sqlquery."\n");
   $ret=DB::query($sqlquery);
   if($table=="output")
   {
      foreach($ret as $k => $row)
      {
         $ret[$k]['relays'] = array();
         $ret[$k]['pwms'] = array();
         $ret[$k]['inputs'] = array();
         $ret[$k]['analogs'] = array();
         if(intval($row['has_relays'])>0) {
            $ret[$k]['relays'] = getPanelIO('relay', $ret[$k]['domain'], $websection, $activeonly,
                                    "relay.board_ip='".$row['board_ip']."' AND relay.outnum='".$row['outnum']."' and relay.outtype='".$row['outtype']."'",
                                    "position,button_name");
         }
         if(intval($row['has_pwms'])>0) {
            $ret[$k]['pwms'] = array();
         }
         $wheredomain_inp="(DMDOMAIN(input.inpname, '".$ret[$k]['domain']."')=1";
         $wheredomain_ana="(DMDOMAIN(analog.ananame, '".$ret[$k]['domain']."')=1";
         if(strlen($ret[$k]['domain'])<=28) {
            $wheredomain_inp.=" OR DMDOMAIN(input.inpname, '".$ret[$k]['domain'].".[*]')=1";
            $wheredomain_ana.=" OR DMDOMAIN(analog.ananame, '".$ret[$k]['domain'].".[*]')=1";
         }
         elseif(strlen($ret[$k]['domain'])<=30) {
            $wheredomain_inp.=" OR DMDOMAIN(input.inpname, '".$ret[$k]['domain'].".*')=1";
            $wheredomain_ana.=" OR DMDOMAIN(analog.ananame, '".$ret[$k]['domain'].".*')=1";
         }
         $wheredomain_inp.=")";
         $wheredomain_ana.=")";
         $ret[$k]['inputs'] = getPanelIO('input', "", "*", $activeonly,
                              $wheredomain_inp, "id", $limit);
         $ret[$k]['analogs'] = getPanelIO('analog', "", "*", $activeonly,
                              $wheredomain_ana, "id", $limit);

      }
   }
   //print_r($ret);
   return $ret;
}


function getPanelActions($table, $content, $websection, $activeonly=true)
{
   $sqlquery="SELECT $table.*,'$table' as devtype,$add FROM $table";
}

function getPanelButtons($user, $content, $sections="*", $websection="*", $selector='dmdomain',$activeonly=true, $limit="")
{
   $buts=array();
   if($sections=='*') {
      $sectar=array('relay','input','analog','output','actions');
   } else {
      $sectar=explode(",",str_replace(" ","",$sections));
   }
   if($selector=="dmdomain")
   {
      foreach($sectar as $sect)
      {
         $res=array();
         switch($sect)
         {
            case "relay":
               $res=getPanelIO("relay",$content, $websection, $activeonly, "", "", $limit);
               $buts=$buts+$res;
               break;
            case "input":
               $res=getPanelIO("input", $content, $websection, $activeonly, "", "", $limit);
               $buts=$buts+$res;
               break;
            case "analog":
               $res=getPanelIO("analog", $content, $websection, $activeonly, "", "", $limit);
               $buts=$buts+$res;
               break;
            case "output":
               $res=getPanelIO("output",$content, $websection, $activeonly, "", "", $limit);
               $buts=$buts+$res;
               break;
            case "actions":
               $res=getPanelIO("actions",$content, $websection, $activeonly, "", "", $limit);
               $buts=$buts+$res;
               break;

         }
      }
   }
   return $buts;
}


?>
