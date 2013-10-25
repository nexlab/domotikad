<? @include_once("../includes/common.php"); ?>
   <div class="insider">
<?

$panels = array();
$panels[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Actions"),'panel_sections'=>'actions','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;
$panels[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Outputs"),'panel_sections'=>'output','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;
$panels[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Inputs"),'panel_sections'=>'input','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'50%')+$PANELDEFAULTS;
$panels[]=array('panel_title'=>$tr->Get($GUISUBSECTION)." - ".$tr->Get("Analogs"),'panel_sections'=>'analog','panel_websections'=>$GUISUBSECTION,'panel_cols'=>4, 'panel_height'=>'50%')+$PANELDEFAULTS;

foreach($panels as $panel) {
      if(file_exists($FSPATH."/panels/head/".$panel['panel_type'].".php"))
         addHead($FSPATH."/panels/head/".$panel['panel_type'].".php");
      if(file_exists($FSPATH."/panels/content/".$panel['panel_type'].".php"))
         include($FSPATH."/panels/content/".$panel['panel_type'].".php");
      if(file_exists($FSPATH."/panels/footjs/".$panel['panel_type'].".php"))
         addFootJS($FSPATH."/panels/footjs/".$panel['panel_type'].".php");
}
?>
   </div> <!-- insider -->
