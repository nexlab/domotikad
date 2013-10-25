<? @include_once("../includes/common.php"); ?>
   <div class="row insider">
<?

$DEFPANELS = array();
$DEFPANELS[]=array('panel_title'=>'Azioni Home','panel_sections'=>'actions','panel_websections'=>'home','panel_height'=>'100%')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>'Uscite Home','panel_sections'=>'relay','panel_websections'=>'home','panel_height'=>'100%')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>'Ingressi Home','panel_sections'=>'input','panel_websections'=>'window','panel_height'=>'100%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Analogiche Home','panel_sections'=>'analog','panel_websections'=>'home','panel_height'=>'50%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Output tapparelle','panel_sections'=>'output','panel_websections'=>'blind','panel_height'=>'50%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Timers','panel_sections'=>'timers','panel_height'=>'50%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Scenari','panel_websection'=>'scenary','panel_height'=>'50%')+$PANELDEFAULTS;

$panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='actuations' ORDER by panel_position,id");
if(!$panels or count($panels)<1) {
   $panels=$DEFPANELS;
   foreach($panels as $p) {
      $q="INSERT INTO user_gui_panels 
         (user,page,panel_title,panel_type,panel_cols,panel_height,panel_visible,panel_position,panel_sections,panel_websections,panel_selector,panel_content)
         VALUES
         ('".$_DOMOTIKA['username']."','actuations','".$p['panel_title']."','".$p['panel_type']."',
            '".$p['panel_cols']."','".$p['panel_height']."','".$p['panel_visible']."','".$p['panel_position']."',
            '".$p['panel_sections']."','".$p['panel_websections']."','".$p['panel_selector']."','".$p['panel_content']."')";
      DB::query($q);
   }

}
foreach($panels as $panel) {
      if(file_exists($FSPATH."/panels/head/".$panel['panel_type'].".php"))
         addHead($FSPATH."/panels/head/".$panel['panel_type'].".php");
      if(file_exists($FSPATH."/panels/content/".$panel['panel_type'].".php"))
         include($FSPATH."/panels/content/".$panel['panel_type'].".php");
      if(file_exists($FSPATH."/panels/footjs/".$panel['panel_type'].".php"))
         addFootJS($FSPATH."/panels/footjs/".$panel['panel_type'].".php");
}
?>
   </div> <!-- row -->
