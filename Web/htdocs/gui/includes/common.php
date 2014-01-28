<?
$GUIDEBUG=FALSE;
//$GUIDEBUG=TRUE;

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

//print_r($_DOMOTIKA);

switch($_DOMOTIKA['left_bar'])
{
   case 'all': $LBAR=array('small','medium','big'); break;
   case 'visible-sm': $LBAR=array('small'); break;
   case 'visible-md': $LBAR=array('medium'); break;
   case 'visible-lg': $LBAR=array('big'); break;
   case 'hidden-sm': $LBAR=array('medium','big'); break;
   case 'hidden-md': $LBAR=array('small','big'); break;
   case 'hidden-lg': $LBAR=array('small','medium'); break;
   case 'none': $LBAR=array(); break;
   default: $LBAR=array('medium','big'); 
}
switch($_DOMOTIKA['right_bar'])
{
   case 'all': $RBAR=array('small','medium','big'); break;
   case 'visible-sm': $RBAR=array('small'); break;
   case 'visible-md': $RBAR=array('medium'); break;
   case 'visible-lg': $RBAR=array('big'); break;
   case 'hidden-sm': $RBAR=array('medium','big'); break;
   case 'hidden-md': $RBAR=array('small','big'); break;
   case 'hidden-lg': $RBAR=array('small','medium'); break;
   case 'none': $RBAR=array(); break;
   default: $RBAR=array('medium','big'); 
}  



$lang=$_DOMOTIKA['language'];
$tr = new Translations($lang);
$img = new Translations("icons");
$PAGE_BUFFER = array();
$PAGE_ADDHEAD = "";
$PAGE_ADDFOOTJS = "";
$PAGE_ADDLEFT = "";
$PAGE_ADDRIGHT = "";

$SHOW_EMPTY_PANELS=TRUE;

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

function notifyListItem($addclass='')
{
   $ret='<a class="list-group-item notify-swipe-deletable '.$addclass.'" id="notifyid-[NID]" href="#">';
   $ret.='  <h4 class="list-group-item-heading">From: [NSOURCE]<i class="glyphicon glyphicon-remove pull-right notify-deletable"></i></h4>';
   $ret.='  <p class="list-group-item-text">[NDATE]</p>';
   $ret.='  <p class="list-group-item-text">[TXT]</p>';
   $ret.='</a>';
   return $ret;
}


?>
