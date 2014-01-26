<? @include_once("../includes/common.php"); ?>
   <div class="left-drawer">
      <div id="websectionlist" class="panel drawer-container scrollable">
         <a href="<?=$BASEGUIPATH."/stats"?>" class="btn btn-block btn-default">Stats Home</a>
<?
   $l=DB::query("SELECT websection FROM stats_charts WHERE websection!='home' group by websection order by websection");
   foreach($l as $k => $v)
   {
      ?>
         <a href="<?=$BASEGUIPATH."/stats/".$v['websection']?>" class="btn btn-block btn-default"><?=$v['websection']?></a>
      <?
   }
?>
      </div>
   </div> 
