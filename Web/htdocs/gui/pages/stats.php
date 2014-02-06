<? @include_once("../includes/common.php"); ?>
   <div class="row insider">
<?

$panels=FALSE;
if($GUISUBSECTION!="")
{
   $v=DB::query("SELECT * FROM stats_charts WHERE websection='$GUISUBSECTION' AND active=1 order by webposition,id");
   if(is_array($v) && count($v)>0) {
      $panels=array();
      $pos=1;
      foreach($v as $pan) {
         $panels[]=array('panel_title'=>"Stats $GUISUBSECTION",'panel_type'=>'graph','panel_content'=>'*','panel_websections'=>"$GUISUBSECTION",
                         'panel_cols'=>'12','panel_height'=>'100%')+$PANELDEFAULTS;
         $pos++;
      }
   }

}
$DEFPANELS = array();
$DEFPANELS[]=array('panel_title'=>'Default stats','panel_type'=>'graph','panel_content'=>'*','panel_websections'=>'home','panel_cols'=>'12','panel_height'=>'100%')+$PANELDEFAULTS;

if(!$panels)
   $panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='stats' ORDER by panel_position,id");

if(!$panels or count($panels)<1) {
   
   $panels=$DEFPANELS;
   foreach($panels as $p) {
      $q="INSERT INTO user_gui_panels 
         (user,page,panel_title,panel_type,panel_cols,panel_height,panel_visible,panel_position,panel_sections,panel_websections,panel_selector,panel_content)
         VALUES
         ('".$_DOMOTIKA['username']."','stats','".$p['panel_title']."','".$p['panel_type']."',
            '".$p['panel_cols']."','".$p['panel_height']."','".$p['panel_visible']."','".$p['panel_position']."',
            '".$p['panel_sections']."','".$p['panel_websections']."','".$p['panel_selector']."','".$p['panel_content']."')";
      DB::query($q);
   }

}
include($FSPATH."/panels/include.php");
?>
   </div> <!-- row -->
