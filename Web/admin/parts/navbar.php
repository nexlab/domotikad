<?
include_once("common_includes.php");
?>
<?
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
?>
<div class="navbar navbar-fixed-top">
  <div class="container">

    <!-- .navbar-toggle is used as the toggle for collapsed navbar content -->
    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-responsive-collapse">
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
    </button>

    <!-- Be sure to leave the brand out there if you want it shown -->
    <a class="navbar-brand" href="/admin/">Domotika Admin</a>

    <!-- Place everything within .navbar-collapse to hide it until above 768px -->
    <div class="nav-collapse collapse navbar-responsive-collapse">
      <ul class="nav navbar-nav">
         <li <?=isActive(array("/admin/", "/admin/index.php"));?>><a href="/admin/">Dashboard</a></li>
         <li <?=isActive(array("/admin/qsystem.php","/admin/boards.php"));?> class="drowdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">
               Systems <span class="caret"></span>
            </a>
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
               <li <?=isActive("/admin/qsystem.php");?>><a href="/admin/qsystem.php">Q System</a></li>
               <li <?=isActive("/admin/boards.php");?>><a href="/admin/boards.php">Boards</a></li>
            </ul>
         </li>
         <li <?=isActive(array("/admin/timers.php","/admin/actions.php","/admin/sequences.php"));?>class="drowdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">
               Automations <span class="caret"></span>
            </a>
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
               <li <?=isActive("/admin/timers.php");?>><a href="/admin/timers.php">Timers</a></li>
               <li <?=isActive("/admin/actions.php");?>><a href="/admin/actions.php">Actions</a></li>
               <li <?=isActive("/admin/sequences.php");?>><a href="/admin/sequences.php">Sequences</a></li>
            </ul>
         </li>
         <li <?=isActive(array());?>class="drowdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">
               Media <span class="caret"></span>
            </a>
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
               <li <?=isActive("/admin/telephony.php");?>><a href="/admin/telephony.php">Telephony</a></li>
               <li <?=isActive("/admin/telephony.php");?>><a href="/admin/telephony.php">Citophony</a></li>
               <li <?=isActive("/admin/audiovideo.php");?>><a href="/admin/audiovideo.php">Audio/Video</a></li>
            </ul>
         </li>
         <li <?=isActive("/admin/stats.php");?>><a href="/admin/stats.php">Stats</a></li>
         <li <?=isActive("/admin/users.php");?>><a href="/admin/users.php">Users</a></li>
      </ul>
      <ul class="nav navbar-nav pull-right">
         <li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">
              <?=$_DOMOTIKA['username']?> <i class="glyphicon glyphicon-user"></i>
            </a>
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
               <li><a href="#">Settings</a></li>
               <li><a href="<?=$_DOMOTIKA['homepath']?>">user gui</a></li>
               <li><a href="/__LOGOUT__/">Logout</a></li>
            </ul>
         </li>
      </ul>
   </div><!-- /.nav-collapse -->
  </div><!-- /.container -->
</div><!-- /.navbar -->
