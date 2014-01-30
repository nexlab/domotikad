<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH?>/" data-guisubsection='' class="btn btn-block btn-default leftbtn" <? /* style="background-image: url(/resources/icons/home_white_alpha_32x32.png)" */?>>home</a>
<?
   $links=array();
   foreach(getWebSections(array('home'), array(), 'devsection') as $ws)
   {
      $links[$tr->Get($ws)]=$ws;
   }
   ksort($links, SORT_NATURAL | SORT_FLAG_CASE);
   $nonelink=false;
   foreach($links as $k => $v)
   {
      if(!startsWith($v, '_')) {
         if($v!='none') {
      ?>
         <a href="<?=$BASEGUIPATH."/actuations/".$v?>" data-guisubsection='<?=$v?>' class="btn btn-block btn-default leftbtn"><?=$k?></a>
      <?
         } else {
            $nonelink=true;
         }
      }
   }
   if($nonelink)
   {
      ?>
         <a href="<?=$BASEGUIPATH."/actuations/none"?>" data-guisubsection='none' class="btn btn-block btn-default leftbtn"><?=$tr->Get('none')?></a>
      <?
   }
?>
      </div>
   </div> 
