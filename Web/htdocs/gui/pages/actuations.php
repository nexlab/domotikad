<? @include_once("../includes/common.php"); ?>
   <div class="insider">
<?

$paneldimensions=array('dimensions' => array(4 => '50%'));
$SHOW_EMPTY_PANELS=FALSE;

if($GUISUBSECTION=="")
   header("Location: $BASEGUIPATH");

$DEFPANELS = array();
$DEFPANELS[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Actions"),'panel_sections'=>'actions','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Outputs"),'panel_sections'=>'output','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Inputs"),'panel_sections'=>'input','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;
$DEFPANELS[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Analogs"),'panel_sections'=>'analog','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;

$panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='actuations' and subpage='$GUISUBSECTION' ORDER by panel_position,id");
if(!$panels or count($panels)<1) {
      $panels=$DEFPANELS;
}

include($FSPATH."/panels/include.php");
?>
   </div> <!-- insider -->
