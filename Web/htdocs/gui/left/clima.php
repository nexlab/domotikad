<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH."/clima"?>" data-guisubsection='' class="btn btn-block btn-default">Clima Home</a>
<?
   $v=DB::query("SELECT id,name,button_name FROM thermostats WHERE active='yes'");
   $links=array();
   foreach($v as $the)
   {
      $links[$the['name']]=$the['button_name'];
   }
   ksort($links, SORT_NATURAL | SORT_FLAG_CASE);
   foreach($links as $k => $v)
   {
      ?>
         <a href="<?=$BASEGUIPATH."/clima/".$k?>" data-guisubsection='<?=$k?>' class="btn btn-block btn-default"><?=$v?></a>
      <?
   }
?>
      </div>
   </div> 
