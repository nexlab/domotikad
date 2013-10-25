<?
include_once("common_includes.php");
include_once("include.php");
?>
<html>
<head title="Domotika GUI">
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
   <script src="/resources/js/jquery-migrate-1.0.0.min.js" type="text/javascript" ></script>
   <script src="/resources/js/sockjs-0.3.min.js" ></script>
   <script src="/resources/js/ajaxsocket.js" ></script>
   <style>
   </style>
</head>
<body>
<? 
   $ret = DB::query("SELECT * FROM users WHERE username='".$_DOMOTIKA['username']."' limit 1");
   $user = $ret[0];
?>
<script type="text/javascript">
$(document).ready(function(){
   if($(window).width() < 800){
      window.location = '<?=$user['mobile_homepath']?>';
   } else {
      window.location = '<?=$user['desktop_homepath']?>';
   }
}); 
</script>
</body>
</html>
