<? @include_once("../../includes/common.php"); ?>
<? 
if($panel && is_array($panel)) { 
   $thermo=DB::queryFirstRow("SELECT * from thermostats WHERE name=%s AND active='yes'", $panel['panel_content']);
   $buttonar=getPanelButtons($_DOMOTIKA['username'],$thermo['sensor_domain'],$panel['panel_sections'],$panel['panel_websections'],$panel['panel_selector'],true);

   $climastatus=DB::queryOneField("value", "SELECT * FROM uniques WHERE name='climastatus'");
   if(!$climastatus) { 
      DB::insert('uniques', array('name'=>'climastatus','value'=>'WINTER'));
      $climastatus='WINTER';
   }
   $climastatuses=DB::query("SELECT DISTINCT(clima_status) FROM thermostats_progs group by clima_status");

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
                  //$_SESSION['PANELS_CHARTS'][$chart['name']."-".$panel['id']]=$chart;
            ?>
               <div style="width:100%;margin:0 auto;text-align:center;" class="devlist-item devlist-item-theme-<?=$_DOMOTIKA['gui_theme']?>">
                  <div>
                     <button type="button" data-domotika-type="btn-choosestatuses" 
                        id="thermo-btnchoosestatus-<?=$button['id']."-".$panel['id']?>"
                        class="btn btn-primary" style="width:150px;height:40px;"><b><?=$climastatus?></b>
                        <i class="glyphicon glyphicon-chevron-down"></i>
                     </button>
                  </div>
                  <div  id="thermo-statuschooselist-<?=$button['id']."-".$panel['id']?>"
                      class="panel panel-theme-<?=$_DOMOTIKA['gui_theme']?> thermo-statuspanel text-on-white-theme-<?=$_DOMOTIKA['gui_theme']?>">
                      <div class="notifylist">
                         <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>" data-snap-ignore="true">
                            <? foreach($climastatuses as $cs) { ?>
                               <button type="button" style="width:100%;margin-top:5px;"
                                       data-domotika-statusselect="<?=$cs['clima_status']?>"
                                       data-domotika-type="statusselect"
                                       data-domotika-panel="thermo-statuschooselist-<?=$button['id']."-".$panel['id']?>"
                                       class="btn btn-success"><?=$cs['clima_status']?></button>
                            <? } ?>
                         </div>
                      </div>
                   </div>
                  <div style="display:inline-block;margin:0 auto;text-align:center;">
                     <div id="gauge-<?=$button['id']."-".$panel['id']?>" data-domotika-type="gauge" 
                        data-dmval-min="<?=floatval($button['minval'])?>"
                        data-dmval-max="<?=floatval($button['maxval'])?>"
                        data-dmval-low="0.0"
                        data-dmval-high="<?=floatval($thermo['setval'])*floatval($button['divider'])?>"
                        data-dmval-divider="<?=floatval($button['divider'])?>"
                        data-dmcolor-min="blue"
                        data-dmcolor-low="blue"
                        data-dmcolor-medium="blue"
                        data-dmcolor-high="red"
                        data-domotika-name="<?=$button['button_name']?>"
                        data-dmval="<?=floatval($button['status'])?>"
                        data-domotika-label="<?=$button['unit']?>"
                        data-domotika-gaugeid="<?=$button['id']?>" style="height:250px;min-width:240px;margin:0 auto;text-align:center;">
                     </div>
                   </div>
                   <div style="display:inline-block;width:20%;min-width:68px;height:250px;margin:0 auto;text-align:center;">
                      <div><button type="button" id="thermo-showset-<?=$button['id']."-".$panel['id']?>" class="btn btn-gray">--.-</button></div>
                      <div style="margin:0 auto;text-align:center;height:150px;margin-top:25px;margin-bottom:25px;"
                           data-domotika-maxval="<?=$thermo['maxslide']?>"
                           data-domotika-minval="<?=$thermo['minslide']?>" 
                           data-domotika-setval="<?=$thermo['setval']?>"
                           id="thermo-level-<?=$button['id']."-".$panel['id']?>" data-domotika-type="thermo-level">
                      </div>
                      <div class="btn-group">
                        <button type="button" class="btn btn-primary btn-small"
                              id="thermo-minus-<?=$button['id']."-".$panel['id']?>">
                              <i class="glyphicon glyphicon-chevron-down"></i></button>
                        <button type="button" class="btn btn-danger btn-small"
                              id="thermo-plus-<?=$button['id']."-".$panel['id']?>">
                              <i class="glyphicon glyphicon-chevron-up"></i></button>
                     </div>
                   </div>
                  <div style="margin-top:45px;">
                     <button type="button" class="btn btn-gray " 
                        id="thermo-btnmanual-<?=$button['id']."-".$panel['id']?>"
                        data-dmcolor-on="btn-primary"
                        data-dmcolor-off="btn-gray"
                        data-domotika-type="btnmanual"
                        style="width:150px;height:40px;"><b>Manual</b></button>
                     <button type="button" class="btn btn-primary " 
                        id="thermo-btnprogram-<?=$button['id']."-".$panel['id']?>"
                        data-dmcolor-on="btn-primary"
                        data-dmcolor-off="btn-gray"
                        data-domotika-type="btnprogram"
                        style="width:150px;height:40px;"><b>Program</b></button>
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
