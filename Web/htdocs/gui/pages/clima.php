<? @include_once("../includes/common.php"); ?>
   <div class="insider">
<?

$paneldimensions=array('dimensions' => array(4 => '50%'));
$SHOW_EMPTY_PANELS=FALSE;

if($GUISUBSECTION=="")
{
   $panels = array();

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Actions"),'panel_sections'=>'actions',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Outputs"),'panel_sections'=>'output',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Inputs"),'panel_sections'=>'input',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;

   $panels[]=array('panel_title'=>$tr->Get('clima')." - ".$tr->Get("Analogs"),'panel_sections'=>'analog',
                  'panel_websections'=>'clima','panel_cols'=>4, 'panel_height'=>'100%')+$PANELDEFAULTS+$paneldimensions;
} else {
   
}
include($FSPATH."/panels/include.php");
?>
   </div> <!-- insider -->
