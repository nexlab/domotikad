<? @include_once("../../includes/common.php"); ?>
<? 
$_SESSION['PANELS_CHARTS']=array();
if($panel && is_array($panel)) { 
   $days = getLastNDays(7, 'Y-m-d' );
   $daysql = getLastNDays(7, 'Y-m-d');
   if($panel['panel_websections']!="" && $panel['panel_websections']!="*") {
      $ws=" AND (";
      $wss=explode(",", $panel['panel_websections']);
      $cws=count($wss);
      $cwsc=1;
      foreach($wss as $w) {
         $ws.="websection='$w'";
         if($cwsc<$cws)
            $ws.=" OR ";
         $cwsc++;
      }
      $ws.=")";
   }
   $charts=DB::query("SELECT * FROM stats_charts WHERE active=1 AND DMDOMAIN(name, '".$panel['panel_content']."')=1 $ws order by webposition");
   if(is_numeric($panel['panel_height'])) $panel['panel_height'].="px";
   $visible="";
   if($panel['panel_visible']!="all") $visible=$panel['panel_visible'];
   if(count($buttonar)<=0) {
      $visible.=" hidden-xs hidden-sm";
   }
?>
      <div class="panel panel-theme-<?=$_DOMOTIKA['gui_theme']?> col-lg-<?=$panel['panel_cols']?> panel-media-low <?=$visible?>" style="height:<?=$panel['panel_height'];?>;">
<?
   if($panel['panel_title']!="") {
?>
         <div class="panel-heading panel-head-theme-<?=$_DOMOTIKA['gui_theme']?>"><h2 class="panel-title"><?=$panel['panel_title']?></h2></div>
   <? } 
   $height="";
   $dmfull="";
   if($panel['panel_height']!="" && intval($panel['panel_height'])>0) {
      $height="style=\"height:".$panel['panel_height']."\"";
      $dmheight="style=\"height:".strval(intval($panel['panel_height'])-70)."px\"";
      if(endsWith($panel['panel_height'], '%')) {
            $dmfull="domotika-panel-full";
            $dmheight="style=\"height:100%;\"";
      }
   }
   elseif($panel['panel_height']!="" && intval($panel['panel_height'])==0) {
      $height="style=\"height:100%;\"";
      $dmfull="domotika-panel-full";
      $dmheight="style=\"height:100%;\"";
   }
?>
    <div class="domotika-panel <?=$dmfull;?>" <?=$dmheight;?>>
      <div class="home-panel chartpanel" <?=$dmheight;?> >
         <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>" >
<?
   foreach($charts as $chart) {
      //print_r($chart);
      $_SESSION['PANELS_CHARTS'][$chart['name']."-".$chart['id']]=$chart;
   ?>
      <div id="<?=$chart['name']."-".$chart['id']?>" style="height:200px;width:550px"></div>
      
<?
   }?>
         </div>
      </div>
    </div>
 
    </div>
<?}?>

