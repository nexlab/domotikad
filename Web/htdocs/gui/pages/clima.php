<? @include_once("../includes/common.php"); ?>
   <div class="row insider">
<?

$DEFPANELS = array();
$DEFPANELS[]=array('panel_title'=>'clima','panel_type'=>'clima','panel_sections'=>'','panel_websections'=>'home','panel_cols'=>6,'panel_height'=>'100%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Uscite Home','panel_sections'=>'relay','panel_websections'=>'home','panel_height'=>'100%')+$PANELDEFAULTS;
//$DEFPANELS[]=array('panel_title'=>'Ingressi Home','panel_sections'=>'input','panel_websections'=>'window','panel_height'=>'100%')+$PANELDEFAULTS;

$panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='clima' ORDER by panel_position,id");
if(!$panels or count($panels)<1) {
   $panels=$DEFPANELS;
   /*
   foreach($panels as $p) {
      $q="INSERT INTO user_gui_panels 
         (user,page,panel_title,panel_type,panel_cols,panel_height,panel_visible,panel_position,panel_sections,panel_websections,panel_selector,panel_content)
         VALUES
         ('".$_DOMOTIKA['username']."','clima','".$p['panel_title']."','".$p['panel_type']."',
            '".$p['panel_cols']."','".$p['panel_height']."','".$p['panel_visible']."','".$p['panel_position']."',
            '".$p['panel_sections']."','".$p['panel_websections']."','".$p['panel_selector']."','".$p['panel_content']."')";
      //DB::query($q);
   }
   */

}
include($FSPATH."/panels/include.php");
?>
   </div> <!-- row -->
