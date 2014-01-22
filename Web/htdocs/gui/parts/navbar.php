<?
@include_once("../includes/common.php");
function isActive($name)
{
   if(is_array($name)) {
      foreach($name as $n) {
         if($_SERVER['PHP_SELF']==$n)
            return 'class="active"';
      }
   } else {
      if($_SERVER['PHP_SELF']==$name)
         return 'class="active"';
   }
   return;
}

$themeclass="";
if($_DOMOTIKA['gui_theme']=='dmblack')
   $themeclass="navbar-inverse";

?>
<div id="topbar" class="navbar <?=$themeclass?> navbar-fixed-top">
   <? if($left) { ?>
    <button id="open-left" type="button" class="navbar-open navbar-openleft">
      <i class="glyphicon glyphicon-indent-left"></i>
    </button>
   <? } ?>
    <p class="navbar-title hidden-sm" data-domotika-dragger="true">Domotika GUI - <?=$tr->Get($GUISECTION)?></p>
    <p class="navbar-title visible-sm"><?=$tr->Get($GUISECTION)?></p>
   <? if($right) { ?>
    <button id="open-right" type="button" class="navbar-open navbar-openright">
      <i class="glyphicon glyphicon-indent-right"></i>
    </button>
   <? } ?>
    <ul class="nav navbar-user">
       <li class="dropdown">
          <a class="dropdown-toggle" data-toggle="dropdown" href="#">
            <?=$_DOMOTIKA['username']?> <i class="glyphicon glyphicon-user"></i>
          </a>
          <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
             <? if($GUISECTION!="settings") { ?>
             <li><a href="<?=$BASEGUIPATH?>/settings">Settings</a></li>
             <? } else { ?>
             <li><a href="<?=$BASEGUIPATH?>"/>Domotika GUI</a></li>
             <? } ?>
             <li><a href="/admin/">admin gui</a></li>
             <li id="install_ff" style="display:none"><a id="installbutton">install as webapp</a></li>
             <li><a href="/__LOGOUT__/">Logout</a></li>
          </ul>
       </li>
    </ul>
</div><!-- /.navbar -->
