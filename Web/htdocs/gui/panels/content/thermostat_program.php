<? @include_once("../../includes/common.php"); ?>
<? 
if($panel && is_array($panel)) { 
   $buttonar=DB::query("SELECT * from thermostats WHERE name=%s AND active='yes'", $panel['panel_content']);   
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
   <style>
      .thermo-statuspanel {
         position:absolute;
         top: 42px;
         width: 300px;
         left:50%;
         margin-left:-150px;
         text-align:center;
         box-shadow: -6px 6px 8px #999;
         height: 80%;
         z-index: 11;
         display:none;
      }
   </style>
    <div class="domotika-panel <?=$dmfull;?>" <?=$dmheight;?>>
      <div class="home-panel" <?=$dmheight;?>>
         <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>">     
            <?
            foreach($buttonar as $button) {
               if($button['sensor_type']=='analog') {
                  //$_SESSION['PANELS_CHARTS'][$chart['name']."-".$panel['id']]=$chart;
            ?>
                  <div style="width:100%;margin:0 auto;text-align:center;" class="devlist-item devlist-item-theme-<?=$_DOMOTIKA['gui_theme']?>">
                     <div style="width:100%;margin:0 auto;text-align:center;margin-bottom:10px;">
                        <button type="button" data-domotika-type="btn-statuses" 
                           id="thermo-btnstatus-<?=$button['id']."-".$panel['id']?>"
                           data-domotika-actualstatus="<?=$climastatus?>"
                           data-domotika-btnthermoname="<?=$button['name']?>"
                           class="btn btn-primary" style="width:150px;height:40px;"><b><?=$climastatus?></b>
                           <i class="glyphicon glyphicon-chevron-down"></i>
                        </button>
                     </div>
                     <div  id="thermo-statuslist-<?=$button['id']."-".$panel['id']?>"
                        class="panel panel-theme-<?=$_DOMOTIKA['gui_theme']?> thermo-statuspanel text-on-white-theme-<?=$_DOMOTIKA['gui_theme']?>">
                        <div class="notifylist">
                           <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>" data-snap-ignore="true">
                              <? foreach($climastatuses as $cs) {?>
                                 <button type="button" style="width:100%;margin-top:5px;<?if($cs['clima_status']==$climastatus)echo'display:none';?>"
                                         data-domotika-statuschoose="<?=$cs['clima_status']?>"
                                         data-domotika-type="statuschoose"
                                         data-domotika-panel="thermo-statuslist-<?=$button['id']."-".$panel['id']?>"
                                         class="btn btn-success"><?=$cs['clima_status']?></button>
                              <? }?>
                           </div>
                        </div>
                     </div>
                     <div style="width:100%;margin:0 auto;text-align:center;">
                        <ul class="nav nav-tabs thermotab">
                           <? foreach(array('mon','tue','wed','thu','fri','sat','sun') as $d) { ?>
                           <li><a href="#<?=$d?>" data-toggle="tab"><?=$d?></a></li>
                           <? } ?>
                        </ul>
                        <div class="tab-content">
                           <? foreach(array('mon','tue','wed','thu','fri','sat','sun') as $d) { 
                              $the=DB::queryFirstRow("SELECT * from thermostats_progs WHERE thermostat_name=%s AND day=%s AND clima_status=%s", 
                                                $button['name'], $d, $climastatus);
                              if(!$the) {
                                 DB::insert('thermostats_progs', array('thermostat_name'=>$button['name'], 'day'=>$d, 'clima_status'=>$climastatus));
                                 $the=DB::queryFirstRow("SELECT * from thermostats_progs WHERE thermostat_name=%s AND day=%s AND clima_status=%s",
                                    $button['name'], $d, $climastatus);
                              }
                           ?>
                           <div class="tab-pane thermo-program-pane" data-domotab-thermo="<?=$d?>" id="<?=$d?>" style="padding-top:35px;">
                              <div class="thermo-program-block" id='thermoblock1'>
                              <?  for($i=0;$i<12;$i++) { ?>
                                 <div class="thermo-program-container">
                                    <div class="thermo-program-subcont">
                                       <div class="thermo-program-show" id="thermo-values-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>">
                                          <?=$the['h'.zfill($i,2)]?>
                                       </div>
                                       <button type="button" 
                                          id="thermo-plus-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>" 
                                          class="btn btn-success btn-noUI">
                                          <b>+</b>
                                       </button>
                                       <div class="noUI-thermo-program" data-domotika-thermo-startvalue="<?=$the['h'.zfill($i,2)]?>"
                                          data-domotika-thermo-minslide="<?=$button['minslide']?>"
                                          data-domotika-thermo-maxslide="<?=$button['maxslide']?>"
                                          data-domotika-level-thermoname="<?=$button['name']?>"
                                          data-domotika-level-statusname="<?=$climastatus?>"
                                          data-domotika-level-day="<?=$d?>"
                                          data-domotika-level-hour="<?='h'.zfill($i,2)?>"
                                          id="thermo-levels-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>" data-domotika-type="thermoprogram">
                                       </div>
                                       <button type="button" 
                                          id="thermo-minus-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>" 
                                          class="btn btn-danger btn-noUI">
                                          <b>-</b>
                                       </button>
                                       <div style="font-size:10px;margin-bottom:20px"><?=$i?></div>
                                    </div>
                                 </div>
                              <? } ?>
                              </div>
                              <div class="thermo-program-block" id='thermoblock2'>
                              <?  for($i=12;$i<24;$i++) { ?>
                                 <div class="thermo-program-container">
                                    <div class="thermo-program-subcont">
                                       <div class="thermo-program-show" id="thermo-values-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>">
                                          <?=$the['h'.zfill($i,2)]?>
                                       </div>
                                       <button type="button" 
                                          id="thermo-plus-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>"
                                          class="btn btn-success btn-noUI">
                                          <b>+</b>
                                       </button>
                                       <div class="noUI-thermo-program" data-domotika-thermo-startvalue="<?=$the['h'.zfill($i,2)]?>"
                                          data-domotika-thermo-minslide="<?=$button['minslide']?>"
                                          data-domotika-thermo-maxslide="<?=$button['maxslide']?>"
                                          data-domotika-level-thermoname="<?=$button['name']?>"
                                          data-domotika-level-statusname="<?=$climastatus?>"
                                          data-domotika-level-day="<?=$d?>"
                                          data-domotika-level-hour="<?='h'.zfill($i,2)?>"
                                          id="thermo-levels-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>" data-domotika-type="thermoprogram">
                                       </div>
                                       <button type="button" 
                                          id="thermo-minus-<?=$button['id']."-".$panel['id']."-".$d."-".$i?>"
                                          class="btn btn-danger btn-noUI">
                                          <b>-</b>
                                       </button>
                                       <div style="font-size:10px;margin-bottom:20px"><?=$i?></div>
                                    </div>
                                 </div>
                              <? } ?>
                              </div>
                           </div>
                           <? } ?>
                        </div>
                     </div>

                     <div style="width:100%;margin:0 auto;text-align:center;">
                         <button type="button" id=thermo-reset-<?=$button['id']."-".$panel['id']?> 
                              data-domotika-type=thermo-reset
                              data-domotika-thermostat="<?=$button['name']?>"
                              class="btn btn-success" disabled style="width:150px;height:40px;"><b>RESET CHANGES</b></button>
                         <button type="button" id=thermo-save-<?=$button['id']."-".$panel['id']?>
                              data-domotika-type=thermo-save
                              data-domotika-thermostat="<?=$button['name']?>"
                              class="btn btn-danger" disabled style="width:150px;height:40px;"><b>SAVE & APPLY</b></button>
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
