<? @include_once("../includes/common.php"); ?>
<?
$webspeech="";
if($_DOMOTIKA['webspeech']=='touch')
   $webspeech='x-webkit-speech="x-webkit-speech"';

$themeclass="";
if($_DOMOTIKA['gui_theme']=='dmblack')
   $themeclass="navbar-inverse";

?>
<div class="navbar <?=$themeclass?> navbar-fixed-bottom">
   <a class="navbar-brand" href="http://www.unixmedia.it" target=_blank>Domotika</a>
   <p class="navbar-text hidden-sm"><a href="http://www.unixmedia.it" class="navbar-link" target=_blank>by Unixmedia</a></p>
   <button id="speechbutton" type="button" class="btn btn-default navbar-btn pull-right speechbutton"></button>
   <form id="speech" class="navbar-form footbar-form hidden-sm text-on-white-theme-<?=$_DOMOTIKA['gui_theme']?>"> 
      <input type="text" id="speechinp" name="text" value="" class="form-control" <?=$webspeech?> lang="<?=$_DOMOTIKA['speechlang']?>" placeholder="Command">
   </form> 
   <form id="speechsm" class="navbar-form footbar-form-sm visible-sm"> 
      <input type="text" id="speechinp" name="text" value="" class="form-control" <?=$webspeech?> lang="<?=$_DOMOTIKA['speechlang']?>" placeholder="Command">
   </form> 
   <button id="notifybutton" type="button" class="btn btn-default navbar-btn pull-right notifybutton">
      <span id="notifybadge" class="badge">0</span>
   </button>
   <a class="btn btn-default navbar-btn pull-right homebutton" href="<?=$BASEGUIPATH;?>"></a>

  <div id="notifypanel" class="panel panel-theme-<?=$_DOMOTIKA['gui_theme']?> notifypanel text-on-white-theme-<?=$_DOMOTIKA['gui_theme']?>">
    <div class="panel-heading panel-head-theme-<?=$_DOMOTIKA['gui_theme']?>"><h4>Notifications<i class="glyphicon glyphicon-remove pull-right" id="notify-removeall"></i></h4></div>
    <div class="notifylist">
      <div class="list-group theme-<?=$_DOMOTIKA['gui_theme']?>" data-snap-ignore="true">
         <div class="list-group-item">
            AAAA
         </div>
      </div>
    </div>
  </div>

</div><!-- /.navbar -->

