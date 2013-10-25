<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH."/video"?>" class="btn btn-block btn-default">Video Home</a>
<?
   $v=DB::query("SELECT id,button_name,position FROM video WHERE websection='video' AND active=1 ORDER BY position,id");
   $links=array();
   foreach($v as $cam)
   {
      $links[$cam['button_name']]=$cam['id'];
   }
   ksort($links, SORT_NATURAL | SORT_FLAG_CASE);
   foreach($links as $k => $v)
   {
      ?>
         <a href="<?=$BASEGUIPATH."/video/".$v?>" class="btn btn-block btn-default"><?=$k?></a>
      <?
   }
?>
      </div>
   </div> 
