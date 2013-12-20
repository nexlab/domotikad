<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH?>" class="btn btn-block btn-default">home</a>
<?
   $links=array();
   foreach(getWebSections(array('home'), array(), 'devsection') as $ws)
   {
      $links[$tr->Get($ws)]=$ws;
   }
   ksort($links, SORT_NATURAL | SORT_FLAG_CASE);
   foreach($links as $k => $v)
   {
      if(!startsWith($v, '_')) {
      ?>
         <a href="<?=$BASEGUIPATH."/actuations/".$v?>" class="btn btn-block btn-default"><?=$k?></a>
      <?
      }
   }
?>
      </div>
   </div> 
