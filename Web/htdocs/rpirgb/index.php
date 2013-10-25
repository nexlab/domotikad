<?
include("common_includes.php");
//print_r($_POST);
$timing=0;
if(count($_POST) > 1)
{
   if(is_numeric($_POST['timeout']) && intval($_POST['timeout']) > 0 && intval($_POST['timeout']) <=6000)
      $timing=intval($_POST['timeout']);
      
   switch($_POST['submit'])
   {
      case "WHITE":
         wget("http://localhost:9980/?rgb=white");
         $color="rgb(0,0,0)";
         break;
      case "OFF":
         wget("http://localhost:9980/?rgb=off");
         $color="rgb(255,255,255)";
         break;
      case "CYCLE":
         wget("http://localhost:9980/?rgb=cycle");
         $color="rgb(0,0,0)";
      case "SET":
         if(strlen($_POST[color])==6 || strlen($_POST[color])==3)
         {
            if(strlen($_POST[color])==6)
            {
               $r=hexdec(substr($_POST[color], 0, 2));
               $g=hexdec(substr($_POST[color], 2, 2));
               $b=hexdec(substr($_POST[color], 4, 2));
            } else {
               $r=hexdec(substr($_POST[color], 0, 1).substr($_POST[color], 0, 1));
               $g=hexdec(substr($_POST[color], 1, 1).substr($_POST[color], 1, 1));
               $b=hexdec(substr($_POST[color], 2, 1).substr($_POST[color], 2, 1));
            }
            wget("http://localhost:9980/?rgb=".strval($r).",".strval($g).",".strval($b).",$timing");
            //print_r("http://localhost:9980/?rgb=".strval($r).",".strval($g).",".strval($b).",$timing");
            $color="rgb(".strval($r).",".strval($g).",".strval($b).")";
         }
         break;
      default:
         $color=wget("http://localhost:9980/");
         $color="rgb(".str_replace("RGB:", "", $color).")";
   }
} else {
   $color=wget("http://localhost:9980/");
   $color="rgb(".str_replace("RGB:", "", $color).")";
}
?>
<html>
   <title>Domotika GUI</title>
   <meta charset="utf-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
   <meta content="true" name="HandheldFriendly" />
   <meta content="320" name="MobileOptimized" /> 
   <meta name="apple-mobile-web-app-capable" content="yes">
   <meta name="apple-mobile-web-app-status-bar-style" content="black">
   <meta http-equiv="cleartype" content="on">
   <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">

      <script src="/resources/js/jquery-1.9.0.min.js" type="text/javascript" ></script>
      <script src='/resources/js/spectrum.js'></script>
      <link rel='stylesheet' href='/resources/css/spectrum.css' />
   </head>
   <body style="text-align:center;margin-left:auto;margin-right:auto;display:table">
   <div  style="margin-right:auto;margin-left:auto;height:100px;width:300px;">
   <a href="http://www.unixmedia.it"><img src="/resources/img/logo_unixmedia_white.png"></img></a>
   <div >RGBLamp v1.0</div>
   </div>
   <div id="show" style="width:80px;height:50px;border:1px solid;margin-right:auto;margin-left:auto;background-color:<?=$color?>"></div>
      <form name="colorpick" id="colorpick" action="<?=$_SERVER["PHP_SELF"];?>" method="POST">
      <input type='text' id="flat" value="<?=$color?>" /><br />
         Time (sec):<select id="timing" name="timeout">
            <option value="0">0</option>
            <option value="1">0.1</option>
            <option value="2">0.2</option>
            <option value="3">0.3</option>
            <option value="4">0.4</option>
            <option value="5">0.5</option>
            <option value="6">0.6</option>
            <option value="7">0.7</option>
            <option value="8">0.8</option>
            <option value="9">0.9</option>
            <option value="10">1</option>
            <option value="20">2</option>
            <option value="30">3</option>
            <option value="40">4</option>
            <option value="50">5</option>
            <option value="60">6</option>
            <option value="70">7</option>
            <option value="80">8</option>
            <option value="90">9</option>
            <option value="100">10</option>
            <option value="110">11</option>
            <option value="120">12</option>
            <option value="130">13</option>
            <option value="140">14</option>
            <option value="150">15</option>
            <option value="200">20</option>
            <option value="250">25</option>
            <option value="300">30</option>
            <option value="450">45</option>
            <option value="600">60</option>
            <option value="1200">120</option>
            <option value="1800">180</option>
            <option value="3000">300</option>
            <option value="6000">600</option>
         </select><br />
         <input type="hidden" id="color" name="color" value="" />
         <input type="submit" name="submit" value="WHITE" />
         <input type="submit" name="submit" value="CYCLE" />
         <input type="submit" name="submit" value="SET" />
         <input type="submit" name="submit" value="OFF" />
      </form>
   </body>
   <script type="text/javascript">
$("#flat").spectrum({
    flat: true,
    showInput: true,
    preferredFormat: "rgb",
    chooseText: "SET",
    cancelText: "Cancel",
    showPalette:true,
    showSelectionPalette:true,
    localStorageKey: "rpirgb",
    palette: [
        ['black', 'white'], 
        ['red', 'rgb(0,255,0)','blue'],
        ['rgb(255, 255, 0);', 'rgb(255, 0, 255);', 'rgb(0, 255, 255);']
    ],
   change: function(color) {
            //$("#color").value=color.toHexString(); 
            $("#color").val(color.toHex());
         },
   move: function(color) {
            $("#color").val(color.toHex());
         }
});

function successUpdate(data)
{
   //console.log(data);
   $("#show").css('background-color', data);
}


function updateShow()
{
   $.get("/domotika/rpirgb/get.php","",successUpdate);
}

setInterval(function() {
   updateShow();
   //alert('int');
}, 1000);
   </script>
</html>
