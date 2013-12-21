<html>
<head>
<title>Domotika GMI Interface</title>
<link rel="stylesheet" href="/resources/pure/pure-nr-min.css">
<link href='style.css' type='text/css' rel='stylesheet'>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script language="javascript" src="simpleGMI.js"></script>
<style>
   #antani {
      top: 100px;
      left: 50px;
   }
</style>
<script type="text/javascript">
simpleGMI.fullScreen();
function sarca(data)
{
   alert(data);
}
setInterval(function(){
   simpleGMI.post('http://admin:domotika@q.unixmedia.net/domotika/gmi/style.css', 'aaa=sarca', sarca);
}, 5000);
</script>
</head>
<body>
<div class="pure-g">
   <div class="pure-u-1-3">
      <button class="pure-button pure-button-primary" onclick="simpleGMI.refresh()">REFRESH</button>
   </div>
   <div class="pure-u-1-3">

   </div>
   <div class="pure-u-1-3" style="float:right">
      <button class="pure-button pure-button-primary" onclick="simpleGMI.refresh()">REFRESH</button>
   </div>

</div>

<div class="footer-bar">
<button onClick="simpleGMI.dial(0, 0, 0, 281, '', 1)" class="pure-button pure-button-secondary">
    <img src="img/microphone-little.png"></img>
</button>

</div>
</body>
</html>
