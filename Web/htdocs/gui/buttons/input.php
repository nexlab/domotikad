<?
@include("../includes/common.php");
//print_r($button);
$onTemplate="success";
$button_checked="";
$button_switchar=array(
   IKAP_CTX_LIGHT,
   IKAP_CTX_SOCKET,
   IKAP_CTX_VALVE,
   IKAP_CTX_GENERIC_SWITCH,
   IKAP_CTX_PUMP,
   IKAP_CTX_MOTOR
   );
$button_text=$button['text_off'];
$button_checked="btn-".$dmcolors[$button['color_off']];
if(intval($button['status'])>0) {
   $button_checked="btn-".$dmcolors[$button['color_on']];
   $button_text=$button['text_on'];
}
?>
<div class="devlist-item devlist-item-theme-<?=$_DOMOTIKA['gui_theme']?>">
   <div class="devlist-row">
      <div class="devlist-leftpart">
            <h4 class="devlist-name"><?=$button['button_name']?></h4>
      </div>
      <div class="devlist-rightpart" data-snap-ignore="true">
         <button class="btn devlist-button <?=$button_checked?>" data-domotika-inpid="<?=$button['id']?>" 
            data-dmcolor-on="btn-<?=$dmcolors[$button['color_on']]?>" data-dmcolor-off="btn-<?=$dmcolors[$button['color_off']]?>"
            data-dmtext-on="<?=$button['text_on']?>" data-dmtext-off="<?=$button['text_off']?>"><?=$button_text?></button>
      </div> <!-- devlist-rightpart-->
   </div> <!-- devlist-row -->
</div> <!-- devlist item -->
