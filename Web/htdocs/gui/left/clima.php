<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH."/cameras"?>" data-guisubsection='' class="btn btn-block btn-default">Clima Home</a>
<?
   $v=DB::query("SELECT id,name FROM thermostats WHERE active=1");
   $links=array();
   foreach($v as $the)
   {
      $links[$the['name']]=$the['id'];
   }
   ksort($links, SORT_NATURAL | SORT_FLAG_CASE);
   foreach($links as $k => $v)
   {
      ?>
         <a href="<?=$BASEGUIPATH."/clima/".$k?>" data-guisubsection='<?=$v?>' class="btn btn-block btn-default"><?=str_replace(".", " ", $k)?></a>
      <?
   }
?>
      </div>
   </div> 
