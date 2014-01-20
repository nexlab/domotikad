<? @include_once("../../includes/common.php"); ?>
<?
foreach($panels as $panel)
{
   $paneldo=TRUE;
   $buttonar=FALSE;

   if(file_exists($FSPATH."/panels/panelcheck/".$panel['panel_type'].".php"))
   {
      $paneldo=FALSE;
      include($FSPATH."/panels/panelcheck/".$panel['panel_type'].".php");
   }
   if($paneldo || $SHOW_EMPTY_PANELS)
   {
      $showpanels[] = array('panel' => $panel, 'buttons' => $buttonar);
   }
}
$totpans=count($showpanels);
foreach($showpanels as $panelar)
{
   $buttonar = $panelar['buttons'];
   $panel = $panelar['panel'];
   if(array_key_exists('dimensions', $panel))
   {
      if(array_key_exists($totpans, $panel['dimensions']))
      {
         $panel['panel_height'] = $panel['dimensions'][$totpans];
      }
   }
   if(file_exists($FSPATH."/panels/head/".$panel['panel_type'].".php"))
      addHead($FSPATH."/panels/head/".$panel['panel_type'].".php");
   if(file_exists($FSPATH."/panels/content/".$panel['panel_type'].".php"))
      include($FSPATH."/panels/content/".$panel['panel_type'].".php");
   if(file_exists($FSPATH."/panels/footjs/".$panel['panel_type'].".php"))
      addFootJS($FSPATH."/panels/footjs/".$panel['panel_type'].".php");
}
?>
