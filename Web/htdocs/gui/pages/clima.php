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

   $thermostats=DB::query("SELECT * from thermostats WHERE name=%s AND active='yes'", $GUISUBSECTION);
   foreach($thermostats as $t)
   {
      $panels[]=array('panel_title'=>$t['button_name'],'panel_sections'=>$t['sensor_type'], 'panel_websections'=>'clima', 
                      'panel_type'=>'thermostat', 'panel_content'=>$t['sensor_domain'],'panel_cols'=>5, 'panel_height'=>'80%')+$PANELDEFAULTS;   
      $panels[]=array('panel_title'=>'programmazione '.$t['button_name'],'panel_sections'=>$t['sensor_type'], 'panel_websections'=>'clima',
                      'panel_type'=>'thermostat_program', 'panel_content'=>$t['name'],'panel_cols'=>5, 'panel_height'=>'80%')+$PANELDEFAULTS;

   }
}
include($FSPATH."/panels/include.php");
?>
   </div> <!-- insider -->
