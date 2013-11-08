<?
$BASEGUIPATH=str_replace("/index.php","",$_SERVER['PHP_SELF']);
$FSPATH=realpath(dirname(__FILE__)."/..");
$GUIPATH=str_replace($BASEGUIPATH,'',explode('?',$_SERVER['REQUEST_URI'])[0]);
$sectar=explode("/", $GUIPATH);
$GUISECTION="index";
$GUISUBSECTION="";
if(count($sectar)>1 and $sectar[1]!="")
   $GUISECTION=$sectar[1];
if(count($sectar)>2)
   $GUISUBSECTION=$sectar[2];
if(count($sectar)>3)
   $GUISUBSECTIONOPT=$sectar[3];

$left=FALSE;
$right=FALSE;
if(file_exists("$FSPATH/left/$GUISECTION.php"))
{
   $left=TRUE;
}
if(file_exists("$FSPATH/right/$GUISECTION.php"))
   $right=TRUE;

$PANELDEFAULTS=array(
                  'panel_title'=>'',
                  'panel_cols'=>'4',
                  'panel_height'=>300,
                  'panel_type'=>'standard',
                  'panel_sections'=>'*',
                  'panel_websections'=>'*',
                  'panel_selector'=>'dmdomain',
                  'panel_content'=>'',
                  'panel_visible'=>'all'
               );

$dmcolors=array(
   'green' => 'success',
   'orange' => 'warning',
   'blue' => 'primary',
   'azure' => 'info',
   'red' => 'danger',
   'gray' => 'gray'
);

include_once("common_includes.php");
@include_once("config.php");
include_once("translations.php");
$lang=$_DOMOTIKA['language'];
$tr = new Translations($lang);
$img = new Translations("icons");
$PAGE_BUFFER = array();
$PAGE_ADDHEAD = "";
$PAGE_ADDFOOTJS = "";
$PAGE_ADDLEFT = "";
$PAGE_ADDRIGHT = "";

function addFootJS($file)
{
   ob_start();
   include_once($file);
   $GLOBALS['PAGE_ADDFOOTJS'].=ob_get_clean();
}
function addHead($file)
{
   ob_start();
   include_once($file);
   $GLOBALS['PAGE_ADDHEAD'].=ob_get_clean();
}

function addLeft($file, $sobstitute=false)
{
   ob_start();
   include($file);
   $GLOBALS['PAGE_ADDLEFT'].=ob_get_clean();
   if($sobstitute)
      $GLOBALS['PAGE_BUFFER']['left_drawer']="";

}

function addRight($file, $sobstitute=false)
{
   ob_start();
   include($file);
   $GLOBALS['PAGE_ADDRIGHT'].=ob_get_clean();
   if($sobstitute)
      $GLOBALS['PAGE_BUFFER']['right_drawer']="";
}

function notifyListItem()
{
   $ret='<a class="list-group-item notify-swipe-deletable" id="notifyid-[NID]" href="#">';
   $ret.='  <h4 class="list-group-item-heading">From: [NSOURCE]<i class="glyphicon glyphicon-remove pull-right notify-deletable"></i></h4>';
   $ret.='  <p class="list-group-item-text">[NDATE]</p>';
   $ret.='  <p class="list-group-item-text">[TXT]</p>';
   $ret.='</a>';
   return $ret;
}

function getPanelIO($table, $content, $websection, $activeonly=true, $where="",$orderby="")
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
                              $wheredomain_inp, "id");
         $ret[$k]['analogs'] = getPanelIO('analog', "", "*", $activeonly,
                              $wheredomain_ana, "id");

      }
   }
   //print_r($ret);
   return $ret;
}


function getPanelActions($table, $content, $websection, $activeonly=true)
{
   $sqlquery="SELECT $table.*,'$table' as devtype,$add FROM $table";
}

function getPanelButtons($user, $content, $sections="*", $websection="*", $selector='dmdomain',$activeonly=true)
{
   $buts=array();
   $sectar=explode(",",str_replace(" ","",$sections));
   if($selector=="dmdomain")
   {
      foreach($sectar as $sect)
      {
         $res=array();
         switch($sect) 
         {
            case "relay":
               $res=getPanelIO("relay",$content, $websection, $activeonly);
               $buts=$buts+$res;
               break;
            case "input":
               $res=getPanelIO("input", $content, $websection, $activeonly);
               $buts=$buts+$res;
               break;
            case "analog":
               $res=getPanelIO("analog", $content, $websection, $activeonly);
               $buts=$buts+$res;
               break;
            case "output":
               $res=getPanelIO("output",$content, $websection, $activeonly);
               $buts=$buts+$res;
               break;
            case "actions":
               $res=getPanelIO("actions",$content, $websection, $activeonly);
               $buts=$buts+$res;
               break;

         }
      }
   }
   return $buts;
}

?>
