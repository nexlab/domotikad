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
?>
<?//print_r($button['inputs']);?>
<div class="devlist-item">
   <div class="devlist-row">
      <div class="devlist-leftpart">
         <h4 class="devlist-name"><?=$button['button_name']?></h4>
         <div class="devlist-ledscontainer">
<?
   foreach($button['inputs'] as $inp) {
      $button_text="status";
      $tmpname=ltrim(str_replace($button['button_name'], "", $inp['button_name']));
      if(strlen($inp['text_led'])>0)
         $button_text=$inp['text_led'];
      elseif(strlen($tmpname)>0)
         $button_text=$tmpname;
      $ledcolor="label-".$dmcolors[$inp['color_off']];
      if(intval($inp['status'])>0) $ledcolor="label-".$dmcolors[$inp['color_on']];
?>
            <div class="label <?=$ledcolor?> devlist-leds" data-domotika-inpled="<?=$inp['id']?>"
               data-dmcolor-on="label-<?=$dmcolors[$inp['color_on']]?>" data-dmcolor-off="label-<?=$dmcolors[$inp['color_off']]?>"><?=$button_text?></div>
<? }
   $pbcoln="label-";
   foreach($button['analogs'] as $ana) {
      $button_text="";
      $tmpname=ltrim(str_replace($button['button_name'], "", $ana['button_name']));
      if(strlen($tmpname)>0)
         $button_text=$tmpname;
      $button_text." ".$ana['unit'].": ";
    
      if(floatval($ana['status'])==floatval($ana['minval']))
      {
         $anacol="label-".$dmcolors[$ana['color_min']];
      } elseif(floatval($ana['status'])>floatval($ana['minval']) && floatval($ana['status'])<=floatval($ana['lowval']))
      {
         $anacol="label-".$dmcolors[$ana['color_low']];
      } elseif(floatval($ana['status'])>floatval($ana['lowval']) && floatval($ana['status'])<=floatval($ana['highval']))
      {
         $anacol="label-".$dmcolors[$ana['color_medium']];
      } elseif(floatval($ana['status'])>floatval($ana['highval']))
      {
         $anacol="label-".$dmcolors[$ana['color_high']];
      }
  
?>
            <div class="label <?=$anacol?> devlist-leds" data-domotika-analed="<?=$ana['id']?>"
               data-dmcolor-min="<?=$pbcoln.$dmcolors[$ana['color_min']]?>" data-dmcolor-low="<?=$pbcoln.$dmcolors[$ana['color_low']]?>"
               data-dmcolor-med="<?=$pbcoln.$dmcolors[$ana['color_medium']]?>" data-dmcolor-high="<?=$pbcoln.$dmcolors[$ana['color_high']]?>"
               data-dmval-min="<?=floatval($ana['minval'])?>" data-dmval-low="<?=floatval($ana['lowval'])?>"
               data-dmval-high="<?=floatval($ana['highval'])?>" data-dmval-max="<?=floatval($ana['maxval'])?>"
               data-dmval-divider="<?=floatval($ana['divider'])?>">
               <span><?=$button_text?></span>
               <span data-domotika-anaval="<?=$ana['id']?>"><?=floatval($ana['status'])/$ana['divider']?></span>
            </div>
<? }?>
         </div>      
      </div>
      <div class="devlist-rightpart" data-snap-ignore="true">
<? 
foreach($button['relays'] as $rel) {
   $ampere=$rel['ampere']/10;
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
         <div class="badge devlist-topdata <?=$badgecolor?>" data-domotika-ampcol="<?=$rel['id']?>" style="width:100%;">
         <div style="width:100%;min-width:-moz-fit-content;">
         <? if($rel['has_amp']>0) { ?>
            <span data-domotika-ampid="<?=$rel['id']?>"><?=($rel['ampere']/10);?></span> A
         <?} else { ?>
            <span>No Amp </span>
         <?}?>
         </div>
<?

   if(in_array($rel['ctx'], $button_switchar)) {
      if(intval($rel['status'])>0) $button_checked="checked";
?>
         <div class="make-switch switch-medium devlist-switch" data-on="<?=$dmcolors[$rel['color_on']]?>" 
            data-off="<?=$dmcolors[$rel['color_off']]?>" data-domotika-relid="<?=$rel['id']?>" 
            data-on-label="<?=$rel['text_on']?>" data-off-label="<?=$rel['text_off']?>">
            <input id="tts" type="checkbox" name="tts" <?=$button_checked?>/>
         </div>
<?
   } else {

      $button_text=$rel['text_off'];
      $button_color='btn-'.$dmcolors[$rel['color_off']];
      if(intval($rel['status'])>0) {
         $button_checked='btn-'.$dmcolors[$rel['color_on']];
         $button_text=$rel['text_on'];
      }
?>
         <button class="btn devlist-button <?=$button_checked?>" data-domotika-relid="<?=$rel['id']?>" 
            data-dmcolor-on="btn-<?=$dmcolors[$rel['color_on']]?>" data-dmcolor-off="btn-<?=$dmcolors[$rel['color_off']]?>"
            data-dmtext-on="<?=$rel['text_on']?>" data-dmtext-off="<?=$rel['text_off']?>"
            style="width:100%;width:-moz-available;"><?=$button_text?></button>
<?
   }
?>
         </div>
<?}?>
      </div> <!-- devlist-rightpart-->
   </div> <!-- devlist-row -->
</div> <!-- devlist item -->
