<?
@include("../includes/common.php");
//print_r($button);
$button_checked="";
$badgecolor="badge-".$dmcolors[$button['color2_off']];
$badgetext=$button['text2_off'];
if(intval($button['status2'])>0) { 
   $badgecolor="badge-".$dmcolors[$button['color2_on']];
   $badgetext=$button['text2_on']; 
}
?>
<div class="devlist-item devlist-item-theme-<?=$_DOMOTIKA['gui_theme']?>">
   <div class="devlist-row">
      <div class="devlist-leftpart">
            <h4 class="devlist-name"><?=$button['button_name']?></h4>
      </div>
      <div class="devlist-rightpart" data-snap-ignore="true">
         <div class="badge devlist-topdata <?=$badgecolor?>" data-domotika-act2col="<?=$button['id']?>"
            data-dmcolor-off="badge-<?=$dmcolors[$button['color2_off']]?>" data-dmcolor-on="badge-<?=$dmcolors[$button['color2_on']]?>">
            <div style="width:100%;min-width:-moz-fit-content;"><span data-domotika-act2textid="<?=$button['id']?>"
               data-dmtext-on="<?=$button['text2_on']?>" data-dmtext-off="<?=$button['text2_off']?>"><?=$badgetext;?></span></div>
         
<?
if(@is_array($button_switchar) && in_array($button['ctx'], $button_switchar)) {
   if(intval($button['status'])>0) $button_checked="checked";
?>
         <div class="make-switch switch-medium devlist-switch" 
            data-on="<?=$dmcolors[$button['color_on']]?>" data-off="<?=$dmcolors[$button['color_off']]?>" 
            data-domotika-actid="<?=$button['id']?>" data-on-label="<?=$button['text_on']?>" data-off-label="<?=$button['text_off']?>">
            <input id="tts" type="checkbox" name="tts" <?=$button_checked?>/>
         </div>
<? 
} else { 
   $button_text=$button['text_off'];
   $button_color="btn-".$dmcolors[$button['color_off']];
   if(intval($button['status'])>0) {
      $button_color="btn-".$dmcolors[$button['color_on']];
      $button_text=$button['text_on'];

   }
?>
         <button class="btn devlist-button <?=$button_color?>" data-domotika-actid="<?=$button['id']?>"
            data-dmcolor-on="btn-<?=$dmcolors[$button['color_on']]?>" data-dmcolor-off="btn-<?=$dmcolors[$button['color_off']]?>"
            data-dmtext-on="<?=$button['text_on']?>" data-dmtext-off="<?=$button['text_off']?>"><?=$button_text?></button>
<?
}?>
         </div>
      </div> <!-- devlist-rightpart-->
   </div> <!-- devlist-row -->
</div> <!-- devlist item -->
