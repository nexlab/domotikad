<? @include_once("../../includes/common.php"); ?>
<? 
if($panel && is_array($panel)) { 
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
<? 
   }

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
      <div class="home-panel" <?=$dmheight;?>>
         <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>">     


         </div>
      </div>
    </div>
 </div>
<?}?>
