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
            $buttonar_center=DB::query("SELECT button_name,screenshot FROM mediasources 
                  WHERE websection='citophone' AND active=1 ORDER BY position,id"); // AND DMDOMAIN(button_name, '".$panel['panel_content']."')=1
            break;
         case 'gxv3175_right':
            $buttonar_right=getPanelButtons($_DOMOTIKA['username'], $panel['panel_content'], $panel['panel_sections'], $panel['panel_websections'], $panel['panel_selector'],true,7);
            break;
      }
}

//$buttonar_left=getPanelButtons($_DOMOTIKA['username'], "*","*","_grandstream_left", "dmdomain","true",7);
//$buttonar_right=getPanelButtons($_DOMOTIKA['username'], "*","*","_grandstream_right", "dmdomain","true",7);
//print_r($buttonar_left);
//print_r($buttonar_center);
?>
<html>
<head>
<script type="text/javascript"
src="https://getfirebug.com/firebug-lite.js">
{
    overrideConsole: false,
    startInNewWindow: false,
    startOpened: true,
    enableTrace: true
}
</script>
<title>Domotika GMI Interface</title>
<link rel="stylesheet" href="/resources/pure/pure-nr-min.css">
<link rel="stylesheet" href="/resources/fontawesome/css/font-awesome.min.css">
<link href='style.css' type='text/css' rel='stylesheet'>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="pragma" content="no-cache">
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate, max-age=-1, max-stale=0, post-check=0, pre-check=0">
<meta http-equiv="expires" content="-1">
<!--
<script src="/resources/js/sockjs-0.3.min.js" ></script>
<script src="/resources/js/ajaxsocket.js" ></script>
<script src="/resources/js/jquery-1.9.0.min.js"></script>
<script type="text/javascript" src="http://getfirebug.com/firebug-lite.js"></script>
-->
<script src="/resources/js/zepto.min.js"></script>
<script src="/resources/EventSource/eventsource.js"></script>
<script language="javascript" src="simpleGMI.js"></script> 
<script type="text/javascript">


window.lastAction=new Date().getTime();
simpleGMI.fullScreen();

/**
 * jQuery alterClass plugin
 *
 * Remove element classes with wildcard matching. Optionally add classes:
 *   $( '#foo' ).alterClass( 'foo-* bar-*', 'foobar' )
 *
 * Copyright (c) 2011 Pete Boere (the-echoplex.net)
 * Free under terms of the MIT license: http://www.opensource.org/licenses/mit-license.php
 *
 */
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

/*
function postreply(arg)
{
   console.debug(arg);
} */
/*
var clicksound = new Audio("/domotika/gmi/beep.wav");
clicksound.preload = 'auto';
clicksound.load();

function playClick(volume) {
  var click=clicksound.cloneNode();
  click.volume=volume;
  click.play();
}*/

function butpushed(btype, bid)
{
   window.lastAction=new Date().getTime();
   //playClick(1);
   //simpleGMI.play('/domotika/gmi/beep.wav',0,0,function(data){alert(data)});
   $.post("/rest/v1.2/"+btype+"/setbyid/"+bid+"/json");
   //simpleGMI.post("http://q.unixmedia.net/rest/v1.2/"+btype+"/setbyid/"+bid+"/json", 'gmi=true', postreply);
}

//setInterval(function(){
//   simpleGMI.refresh();
//}, 3600000);
//   simpleGMI.post('http://q.unixmedia.net/domotika/gmi/style.css', 'aaa=sarca', postreply);
//}, 5000);
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
            <button class="pure-button pure-button-primary" style="width:100%;height:130px;" onclick="simpleGMI.refresh()">No Citophones</button>
         <? } else { ?>
         <select class="styled-select" id=camerasel name=camerasel style="width:100%;height:130px;">
            <? foreach($buttonar_center as $cit) { ?>
               <option value="<?=$cit['screenshot'];?>"><?=$cit['button_name']?></option>
            <? } ?>               
         </select>
         <? } ?>
      </div>
      
      <div style="height:80px" onclick="simpleGMI.refresh()">
      </div>
      <div style="padding:5px;display:block">
         <img id="camera" src="/domotika/gmi/img/camera.jpg" style="width:100%;height:190px" onclick="simpleGMI.refresh()"></img>
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

<div class="footer-bar">
<!--
<button onClick="simpleGMI.dial(0, 0, 0, 281, '', 1)" class="pure-button pure-button-secondary">
   <i class="fa fa-microphone fa-2x blackiconcolor"></i>
</button>
<span> STATUS: DEFAULT</span>
<button onClick="simpleGMI.refresh()" class="pure-button pure-button-secondary" style="float:right">
   <i class="fa fa-refresh fa-2x fa-spin blackiconcolor"></i>
</button>
-->
<button onClick="simpleGMI.dial(0, 0, 0, 281, '', 1)" class="pure-button pure-button-secondary">
   <i class="fa fa-microphone fa-2x blackiconcolor"></i>
</button>
<button onClick="simpleGMI.refresh()" class="pure-button pure-button-secondary" style="float:right">
   <i class="fa fa-refresh fa-2x blackiconcolor"></i>
</button>
</div>
<script>
var es = new EventSource("/sse");

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
            //alert(color);
            $(this).alterClass('pure-button-*', color);
         }
      )
   });
}
es.addEventListener("sync", syncReceived);

window.camimage = new Image();
window.camimage.src = "/domotika/gmi/img/camera.jpg";

function updateImage()
{
   if(window.camimage.complete) {
      $('#camera').attr('src', window.camimage.src);
      window.camimage = new Image();
      window.camimage.src = $('#camerasel').val() + "?time=" + new Date().getTime();
      //alert($('#camerasel option:selected').text());
   }
   if(es!=null)
      setTimeout(updateImage, 500);
}

window.camimagenum = <?=count($buttonar_center)?>;


if(window.camimagenum>0)
   updateImage();

keepAlive = setInterval(function(){
   
   $.get("/rest/v1.2/keepalive/json", 
      function(r){
         if(r.data=='SLOGGEDOUT')
         {
            //location.reload();
            simpleGMI.refresh();            
         }
      });
    },5000);

function endGMI()
{
   clearInterval(keepAlive);
   es.close();
   es=null;
   simpleGMI.exit();
}

function checkEnd()
{
   window.checkAction=new Date().getTime();
   if((window.checkAction-window.lastAction)>30000)
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
