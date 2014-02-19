<? @include_once("../includes/common.php"); ?>
   <div class="insider">
<?

$paneldimensions=array('dimensions' => array(4 => '50%'));
$SHOW_EMPTY_PANELS=FALSE;

$panels = array();

if($GUISUBSECTION=="")
{

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Actions"),'panel_sections'=>'actions',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Outputs"),'panel_sections'=>'output',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Inputs"),'panel_sections'=>'input',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Analogs"),'panel_sections'=>'analog',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;
} else {

   $thermostats=DB::query("SELECT * from thermostats WHERE name=%s", $GUISUBSECTION);
   foreach($thermostats as $t)
   {
      $ptype='standard';
      $pname=str_replace(".", " ", $t['name']);
      if($t['sensor_type']=='analog') $ptype='gauge';
      $panels[]=array('panel_title'=>$pname,'panel_sections'=>$t['sensor_type'], 'panel_websections'=>'clima', 
                      'panel_type'=>$ptype, 'panel_content'=>$t['sensor_domain'],'panel_cols'=>4, 'panel_height'=>'50%')+$PANELDEFAULTS;   
   }
}
include($FSPATH."/panels/include.php");
?>
   </div> <!-- insider -->
