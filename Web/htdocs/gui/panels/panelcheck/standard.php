<? @include_once("../../includes/common.php"); ?>
<?
if($panel && is_array($panel)) {
   $buttonar=getPanelButtons($_DOMOTIKA['username'],$panel['panel_content'],$panel['panel_sections'],$panel['panel_websections'],$panel['panel_selector'],true);
   if(count($buttonar) > 0)
      $paneldo=TRUE;
}
?>
