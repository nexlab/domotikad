<? @include_once("../includes/common.php"); ?>
   <div class="row insider">
<?



$DEFPANELS = array();


$panels=FALSE;
if($GUISUBSECTION!="" && is_numeric($GUISUBSECTION))
{
   $pos=1;
   $v=DB::query("SELECT id,button_name,position,videostream,force_input_codec FROM mediasources WHERE websection='camera' AND active=1 AND id='".$GUISUBSECTION."'");
   if(is_array($v) && count($v)>0) {
      $panels=array();
      foreach($v as $cam) {
         $camstream=$cam['videostream'];
         if(strlen($cam['force_input_codec'])>0)
            $camstream.="&icodec=".$cam['force_input_codec'];
         #$panels[]=array('panel_title'=>$cam['button_name'],'panel_position'=>$pos,'panel_content'=>$cam['id'],
         $panels[]=array('panel_title'=>$cam['button_name'],'panel_position'=>$pos,'panel_content'=>$camstream,
            'panel_height'=>'100%','panel_type'=>'cameras')+$PANELDEFAULTS;
         $pos++;
      }
   }
} 

if(!$panels)
   $panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='cameras' ORDER by panel_position,id");


if(!is_array($panels) or count($panels)<1) {
   $v=DB::query("SELECT id,button_name,position,videostream,force_input_codec FROM mediasources WHERE websection='camera' AND  active=1 ORDER BY position,id LIMIT 3");
   if(is_array($v) && count($v)>0) {
      $pos=1;
      foreach($v as $cam) {
         $camstream=$cam['videostream'];
         if(strlen($cam['force_input_codec'])>0)
            $camstream.="&icodec=".$cam['force_input_codec'];
         $DEFPANELS[]=array('panel_title'=>$cam['button_name'],'panel_position'=>$pos,'panel_content'=>$camstream,
                            'panel_height'=>'100%','panel_type'=>'cameras')+$PANELDEFAULTS;
         $pos++;
      }
   }
   $panels=$DEFPANELS;
   foreach($panels as $p) {
      $q="INSERT INTO user_gui_panels 
         (user,page,panel_title,panel_type,panel_cols,panel_height,panel_visible,panel_position,panel_sections,panel_websections,panel_selector,panel_content)
         VALUES
         ('".$_DOMOTIKA['username']."','cameras','".$p['panel_title']."','".$p['panel_type']."',
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
