<?
include_once("common_includes.php");

$DEFPANELS = array();
$DEFPANELS[]=array('panel_title'=>'grandstream_left','panel_websections'=>'_grandstream_left','panel_type'=>'gxv3175_left','panel_content'=>'*')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>'grandstream_center','panel_websections'=>'_grandstream_center','panel_type'=>'gxv3175_center','panel_content'=>'*')+$PANELDEFAULTS;
$DEFPANELS[]=array('panel_title'=>'grandstream_right','panel_websections'=>'_grandstream_right','panel_type'=>'gxv3175_right','panel_content'=>'*')+$PANELDEFAULTS;

$colors=array(
   'gray' => 'pure-button-active',
   'blue' =>  'pure-button-primary', 
   'azure' =>  'pure-button-secondary',
   'green' =>  'pure-button-success',
   'red' => 'pure-button-error',
   'orange' => 'pure-button-warning'
);

$panels=DB::query("SELECT * FROM user_gui_panels WHERE user='$_DOMOTIKA[username]' AND page='gmi' ORDER by panel_position,id");
if(!$panels or count($panels)<1) {
   $panels=$DEFPANELS;
   foreach($panels as $p) {
      $q="INSERT INTO user_gui_panels 
         (user,page,panel_title,panel_type,panel_cols,panel_height,panel_visible,panel_position,panel_sections,panel_websections,panel_selector,panel_content)
         VALUES
         ('".$_DOMOTIKA['username']."','gmi','".$p['panel_title']."','".$p['panel_type']."',
            '".$p['panel_cols']."','".$p['panel_height']."','".$p['panel_visible']."','".$p['panel_position']."',
            '".$p['panel_sections']."','".$p['panel_websections']."','".$p['panel_selector']."','".$p['panel_content']."')";
      DB::query($q);
   }
}
foreach($panels as $panel) {
      switch($panel['panel_type'])
      {
         case 'gxv3175_left':
            $buttonar_left=getPanelButtons($_DOMOTIKA['username'], $panel['panel_content'], $panel['panel_sections'], $panel['panel_websections'], $panel['panel_selector'],true,7);
            break;
         case 'gxv3175_center':
            $buttonar_center=DB::query("SELECT button_name,screenshot,audiostream FROM mediasources 
                  WHERE websection='citophone' AND active=1 ORDER BY position,id"); // AND DMDOMAIN(button_name, '".$panel['panel_content']."')=1
            break;
         case 'gxv3175_right':
            $buttonar_right=getPanelButtons($_DOMOTIKA['username'], $panel['panel_content'], $panel['panel_sections'], $panel['panel_websections'], $panel['panel_selector'],true,7);
            break;
      }
}

?>
<html>
<head>
<title>Domotika GMI Interface</title>
<link rel="stylesheet" href="/resources/pure/pure-nr-min.css">
<link rel="stylesheet" href="/resources/fontawesome/css/font-awesome.min.css">
<link href='style.css' type='text/css' rel='stylesheet'>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate, max-age=-1, max-stale=0, post-check=0, pre-check=0">
<meta http-equiv="expires" content="-1">
<script src="/resources/js/zepto.min.js"></script>
<script src="/resources/EventSource/eventsource.js"></script>
<script language="javascript" src="simpleGMI.js"></script> 
<script type="text/javascript">

window.lastAction=new Date().getTime();
simpleGMI.fullScreen();

(function ( $ ) {
$.fn.alterClass = function ( removals, additions ) {
   var self = this;
   if ( removals.indexOf( '*' ) === -1 ) {
      // Use native jQuery methods if there is no wildcard matching
      self.removeClass( removals );
      return !additions ? self : self.addClass( additions );
   }
   var patt = new RegExp( '\\s' +
         removals.
            replace( /\*/g, '[A-Za-z0-9-_]+' ).
            split( ' ' ).
            join( '\\s|\\s' ) +
         '\\s', 'g' );
   self.each( function ( i, it ) {
      var cn = ' ' + it.className + ' ';
      while ( patt.test( cn ) ) {
         cn = cn.replace( patt, ' ' );
      }
      it.className = $.trim( cn );
   });
   return !additions ? self : self.addClass( additions );
};
})( window.jQuery || window.Zepto );

function butpushed(btype, bid)
{
   window.lastAction=new Date().getTime();
   $.post("/rest/v1.2/"+btype+"/setbyid/"+bid+"/json");
}

function selcamopen()
{
   window.lastAction=new Date().getTime();
   $('#camopts').show();
   $('#camchoose').hide();
   $('#camcall').hide();
}

function changeCamera(uri, name, sip)
{
   window.lastAction=new Date().getTime();
   $('#camchoose').attr('data-uri', uri)
   $('#camchoose').text('CAM: '+name);
   $('#camcall').attr('data-sip', sip);
   $('#camchoose').show();
   $('#camcall').show();
   $('#camopts').hide();
}

function callcam()
{
   window.lastAction=new Date().getTime();
   simpleGMI.dial(0, 1, 0, $('#camcall').attr('data-sip'), '', 0);
}
</script>
</head>
<body>
<div class="pure-g" >
   <div class="pure-u-1-3" style="padding-left:1.3333%;">
      <?
         foreach($buttonar_left as $but) {
            if(intval($but['status'])==1)
               $bcolor=$colors[$but['color_on']];
            else
               $bcolor=$colors[$but['color_off']];
      ?> 
         <div style="padding:5px;">
            <button class="pure-button <?=$bcolor?>" data-dm-type="<?=$but['devtype']?>-<?=$but['id']?>" data-dmcolor-on="<?=$colors[$but['color_on']]?>" data-dmcolor-off="<?=$colors[$but['color_off']]?>" style="width:100%;height:50px;" onclick="butpushed('<?=$but['devtype']?>',<?=$but['id']?>)"><?=$but['button_name']?></button>
         </div>
      <?
         }
      ?>
   </div>
   <div class="pure-u-1-3" style="width:31%">
      <div style="padding:5px;">
         <? if(count($buttonar_center)<1) { ?>
            <button class="pure-button pure-button-warning" style="width:100%;height:130px;" onclick="simpleGMI.refresh()">No Citophones</button>
         <? } else { ?>
               <button class="pure-button pure-button-success" style="width:100%;height:60px;" 
                     data-uri="<?=$buttonar_center['0']['screenshot'];?>" id="camchoose"
                     onclick="selcamopen()">CAM: <?=$buttonar_center['0']['button_name']?></button>
               <button class="pure-button pure-button-warning" style="width:100%;height:60px;margin-top:10px;" 
                     data-sip="<?=str_replace('SIP:','',$buttonar_center['0']['audiostream']);?>" id="camcall"
                     onclick="callcam()">Chiama</button>

               <div style="width:30%;background-color:#000;position:absolute;top:10px;display:none;z-index:1000;overflow:auto;height:85%" id="camopts">
            <? foreach($buttonar_center as $cit) { ?>
               <button class="pure-button pure-button-secondary" 
                  onclick="changeCamera('<?=$cit['screenshot'];?>', '<?=$cit['button_name']?>', '<?=str_replace('SIP:','', $cit['audiostream'])?>')"
                  style="width:100%;height:50px;margin-top:5px;" ><?=$cit['button_name']?></button>
            <? } ?>               
               </div>
         <? } ?>
      </div>
      
      <div style="height:80px" onclick="simpleGMI.refresh()">
      </div>
      <div style="padding:5px;display:block;position:absolute;top:220px;">
         <img id="camera" src="/domotika/gmi/img/camera.jpg" style="width:80%;height:190px" onclick="simpleGMI.refresh()"></img>
      </div>


   </div>
   <div class="pure-u-1-3" >
      <?
         foreach($buttonar_right as $but) {
            if(intval($but['status'])==1)
               $bcolor=$colors[$but['color_on']];
            else
               $bcolor=$colors[$but['color_off']];

      ?>
         <div style="padding:5px;">
            <button class="pure-button <?=$bcolor?>" data-dm-type="<?=$but['devtype']?>-<?=$but['id']?>" data-dmcolor-on="<?=$colors[$but['color_on']]?>" data-dmcolor-off="<?=$colors[$but['color_off']]?>" style="width:100%;height:50px;" onclick="butpushed('<?=$but['devtype']?>',<?=$but['id']?>)"><?=$but['button_name']?></button>
         </div>
      <?
         }
      ?>
   </div>

</div>

<div class="footer-bar" style="z-index:10000">
<button onClick="simpleGMI.dial(0, 0, 0, 281, '', 1)" class="pure-button pure-button-secondary">
   <i class="fa fa-microphone fa-2x blackiconcolor"></i>
</button>
<button onClick="simpleGMI.refresh()" class="pure-button pure-button-secondary" style="float:right">
   <i class="fa fa-refresh fa-2x blackiconcolor"></i>
</button>
</div>
<script>

var syncReceived = function(event) {
   var res=$.parseJSON(event.data);
   $.each(res.data.statuses, function(idx, val){
      console.debug(val);
      $("[data-dm-type="+val[3]+"s-"+val[0]+"]").each(
         function() {
            if(val[1]==1)
               var color=$(this).attr('data-dmcolor-on');
            else
               var color=$(this).attr('data-dmcolor-off');
            $(this).alterClass('pure-button-*', color);
         }
      )
   });
}

window.camimage = new Image();
window.camimage.src = "/domotika/gmi/img/camera.jpg";

function updateImage()
{
   if(window.camimage.complete) {
      $('#camera').attr('src', window.camimage.src);
      window.camimage = new Image();
      window.camimage.src = $('#camchoose').attr('data-uri') + "?time=" + new Date().getTime();
   }
   if(window.es!=null)
      setTimeout(updateImage, 500);
}

window.camimagenum = <?=count($buttonar_center)?>;

Zepto(function($){
   window.es = new EventSource("/sse");
   window.es.addEventListener("sync", syncReceived);
   if(window.camimagenum>0)
      updateImage();
});

keepAlive = setInterval(function(){
   
   $.get("/rest/v1.2/keepalive/json", 
      function(r){
         if(r.data=='SLOGGEDOUT')
         {
            simpleGMI.refresh();            
         }
      });
    },5000);

function endGMI()
{
   clearInterval(keepAlive);
   try {
      es.close();
      es=null;
   } catch(err) {

   }
   simpleGMI.exit();
}

function checkEnd()
{
   window.checkAction=new Date().getTime();
   if((window.checkAction-window.lastAction)>60000)
   {
      endGMI();
   } else { 
      setTimeout(checkEnd, 1000);
   }
      
}

setTimeout(checkEnd, 1000);
setTimeout(endGMI, 900000);
</script>
</body>
</html>
