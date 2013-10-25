<?
@include("../includes/common.php");
//print_r($button);
$button_checked="";
$button_switchar=array(
   IKAP_CTX_LIGHT,
   IKAP_CTX_SOCKET,
   IKAP_CTX_VALVE,
   IKAP_CTX_GENERIC_SWITCH,
   IKAP_CTX_PUMP,
   IKAP_CTX_MOTOR
   );
$ampere=$button['ampere']/10;
$badgecolor="";
if($ampere>0 && $ampere<8) {
   $badgecolor="badge-success";
}elseif($ampere>=8 && $ampere<11) { 
   $badgecolor="badge-info";
}elseif($ampere>=11 && $ampere<14) {
   $badgecolor="badge-warning";
}elseif($ampere>=14) {
   $badgecolor="badge-danger";
}

?>
<div class="devlist-item">
   <div class="devlist-row">
      <div class="devlist-leftpart">
            <h4 class="devlist-name"><?=$button['button_name']?></h4>
      </div>
      <div class="devlist-rightpart" data-snap-ignore="true">
         <div class="badge devlist-topdata <?=$badgecolor?>" data-domotika-ampcol="<?=$button['id']?>">
            <div style="width:100%;min-width:-moz-fit-content;">
            <? if($button['has_amp']>0) { ?>
               <span data-domotika-ampid="<?=$button['id']?>"><?=($button['ampere']/10);?></span> A
            <?} else { ?>
               <span>No Amp </span>
            <?}?>
           </div>
         
<?
if(in_array($button['ctx'], $button_switchar)) {
   if(intval($button['status'])>0) $button_checked="checked";
?>
         <div class="make-switch switch-medium devlist-switch" 
            data-on="<?=$dmcolors[$button['color_on']]?>" data-off="<?=$dmcolors[$button['color_off']]?>" 
            data-domotika-relid="<?=$button['id']?>" data-on-label="<?=$button['text_on']?>" data-off-label="<?=$button['text_off']?>">
            <input id="tts" type="checkbox" name="tts" <?=$button_checked?>/>
         </div>
<? 
} else { 
   $button_text=$button['text_off'];
   $button_color=$dmcolors[$button['color_off']];
   if(intval($button['status'])>0) {
      $button_checked=$dmcolors[$button['color_on']];
      $button_text=$button['text_on'];
   }

?>
         <button class="btn devlist-button <?=$button_checked?>" data-domotika-relid="<?=$button['id']?>"
            data-dmcolor-on="btn-<?=$dmcolors[$button['color_on']]?>" data-dmcolor-off="btn-<?=$dmcolors[$button['color_off']]?>"
            data-dmtext-on="<?=$button['text_on']?>" data-dmtext-off="<?=$button['text_off']?>"><?=$button_text?></button>
<?
}?>
         </div>
      </div> <!-- devlist-rightpart-->
   </div> <!-- devlist-row -->
</div> <!-- devlist item -->
