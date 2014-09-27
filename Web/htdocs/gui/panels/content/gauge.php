<? @include_once("../../includes/common.php"); ?>
<? 
if($panel && is_array($panel)) { 
   $buttonar=getPanelButtons($_DOMOTIKA['username'],$panel['panel_content'],$panel['panel_sections'],$panel['panel_websections'],$panel['panel_selector'],true);
   if(is_numeric($panel['panel_height'])) $panel['panel_height'].="px";
   $visible="";
   if($panel['panel_visible']!="all") $visible=$panel['panel_visible'];
   if(count($buttonar)<=0) {
      $visible.=" hidden-xs hidden-sm";
   }
   if(!array_key_exists('id', $panel))
      $panel['id']=mt_rand();
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
            <?
            foreach($buttonar as $button) {
               if($button['devtype']=='analog') {
            ?>
               <div style="width:100%;">
                  <div id="gauge-<?=$button['id']."-".$panel['id']?>" data-domotika-type="gauge" 
                     data-dmval-min="<?=floatval($button['minval'])?>"
                     data-dmval-max="<?=floatval($button['maxval'])?>"
                     data-dmval-low="<?=floatval($button['lowval'])?>"
                     data-dmval-high="<?=floatval($button['highval'])?>"
                     data-dmval-divider="<?=floatval($button['divider'])?>"
                     data-dmcolor-min="<?=$button['color_min']?>"
                     data-dmcolor-low="<?=$button['color_low']?>"
                     data-dmcolor-medium="<?=$button['color_medium']?>"
                     data-dmcolor-high="<?=$button['color_high']?>"
                     data-domotika-name="<?=$button['button_name']?>"
                     data-dmval="<?=floatval($button['status'])?>"
                     data-domotika-label="<?=$button['unit']?>"
                     data-domotika-gaugeid="<?=$button['id']?>" style="height:200px;width:250px;margin:0 auto;text-align: center;">
                  </div>
               </div>
            <?
               }
            }?>

         </div>
      </div>
    </div>
 </div>
<?}?>
