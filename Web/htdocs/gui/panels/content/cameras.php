<? @include_once("../../includes/common.php"); ?>
<? 
if($panel && is_array($panel)) { 
   if(is_numeric($panel['panel_height'])) $panel['panel_height'].="px";
   $visible="";
   if($panel['panel_visible']!="all") $visible=$panel['panel_visible'];
?>
      <div class="panel col-lg-<?=$panel['panel_cols']?> panel-media-low <?=$visible?>" style="height: auto">
<?
   if($panel['panel_title']!="") {
?>
         <div class="panel-heading"><h2 class="panel-title"><?=$panel['panel_title']?></h2></div>
<? 
   }

   $height="";
   $dmfull="";
   if($panel['panel_height']!="" && intval($panel['panel_height'])>0) {
      $height="style=\"height:".$panel['panel_height']."\"";
      $dmheight="style=\"height:".strval(intval($panel['panel_height'])-30)."px\"";
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
   <div data-swf="/resources/flowplayer/flowplayer.swf"
      class="flowplayer no-toggle"
       data-ratio="0.75" data-embed="false">
      <video autoplay preload="none" loop="true">
         <!--
         <source type="video/webm" src="http://stream.flowplayer.org/bauhaus/624x260.webm"/>
         <source type="video/mp4" src="http://stream.flowplayer.org/bauhaus/624x260.mp4"/>
         <source type="video/ogv" src="http://stream.flowplayer.org/bauhaus/624x260.ogv"/>
         -->
         <source src="/mediaproxy/webm/?uri=<?=$panel['panel_content']?>&direct=true" type="video/webm">
         <!--
         <source src="/mediastream/640x480/h264/15" type="video/mp4">
         <source src="/mediastream/640x480/webm/21" type="video/webm">
         <source src="/mediastream/640x480/theora/21" type="video/ogg">
         -->
         Video Format NOT Supported. Sorry
      </video>

         </div>
      </div>
    </div>
 </div>
<?}?>
