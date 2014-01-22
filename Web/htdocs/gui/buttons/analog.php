<?
@include("../includes/common.php");
//print_r($button);
//$button['status']=900;
//$button['divider']=10;
if(floatval($button['status'])==floatval($button['minval']))
{
   $anacol="progress-bar-".$dmcolors[$button['color_min']];
   $btncol="btn-".$dmcolors[$button['color_min']];
} elseif(floatval($button['status'])>floatval($button['minval']) && floatval($button['status'])<=floatval($button['lowval']))
{
   $anacol="progress-bar-".$dmcolors[$button['color_low']];
   $btncol="btn-".$dmcolors[$button['color_low']];
} elseif(floatval($button['status'])>floatval($button['lowval']) && floatval($button['status'])<=floatval($button['highval']))
{
   $anacol="progress-bar-".$dmcolors[$button['color_medium']];
   $btncol="btn-".$dmcolors[$button['color_medium']];
} elseif(floatval($button['status'])>floatval($button['highval']))
{
   $anacol="progress-bar-".$dmcolors[$button['color_high']];
   $btncol="btn-".$dmcolors[$button['color_high']];
}
$pbcoln="progress-bar-";
$perc=(floatval($button['status'])-floatval($button['minval']))*100/(floatval($button['maxval'])-floatval($button['minval']))
?>
<div class="devlist-item devlist-item-theme-<?=$_DOMOTIKA['gui_theme']?>">
   <div class="devlist-row">
      <div class="devlist-leftpart">
            <h4 class="devlist-name"><?=$button['button_name']?></h4>
            <div class="progress">
               <div class="progress-bar <?=$anacol?>" role="progressbar" aria-valuenow="<?=floatval($button['status'])/$button['divider']?>" aria-valuemin="<?=$button['minval']?>" 
                  aria-valuemax="<?=$button['maxval']?>" style="width: <?=$perc?>%;"
                  data-dmcolor-min="<?=$pbcoln.$dmcolors[$button['color_min']]?>" data-dmcolor-low="<?=$pbcoln.$dmcolors[$button['color_low']]?>"
                  data-dmcolor-med="<?=$pbcoln.$dmcolors[$button['color_medium']]?>" data-dmcolor-high="<?=$pbcoln.$dmcolors[$button['color_high']]?>"
                  data-dmval-min="<?=floatval($button['minval'])?>" data-dmval-low="<?=floatval($button['lowval'])?>"
                  data-dmval-high="<?=floatval($button['highval'])?>" data-dmval-max="<?=floatval($button['maxval'])?>"
                  data-dmval-divider="<?=floatval($button['divider'])?>" data-domotika-anaprog="<?=$button['id']?>">
               <span class="sr-only"><?=floatval($button['status'])/$button['divider']?></span>
            </div>
         </div>
      </div>
      <div class="devlist-rightpart" data-snap-ignore="true">
         <button class="btn devlist-button <?=$btncol?>" data-domotika-anaid="<?=$button['id']?>" 
            data-dmcolor-min="btn-<?=$dmcolors[$button['color_min']]?>" data-dmcolor-low="btn-<?=$dmcolors[$button['color_low']]?>"
            data-dmcolor-med="btn-<?=$dmcolors[$button['color_medium']]?>" data-dmcolor-high="btn-<?=$dmcolors[$button['color_high']]?>"
            ><span><?=$button['unit']?>:</span> <span><?=floatval($button['status'])/$button['divider']?></span></button>
      </div> <!-- devlist-rightpart-->
   </div> <!-- devlist-row -->
</div> <!-- devlist item -->
