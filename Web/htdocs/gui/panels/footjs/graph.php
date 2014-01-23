<? @include_once("../../includes/common.php"); ?>
<script type="text/javascript">
$(document).ready(function() {
<?
$days = getLastNDays(7, 'Y-m-d' );
$daysql = getLastNDays(7, 'Y-m-d');
foreach($_SESSION[PANELS_CHARTS] as $eid => $chart)
{
   $chartserie = getChartData($chart['name']);
   ?>
var plot_<?=$chart['name']?>=$.jqplot('<?=$eid?>', [<?
   $maxseriecount=0;
   for($c=0;$c<count($chartserie);$c++)
   {
      if($maxseriecount<$chartserie[$c]['count'])
         $maxseriecount=$chartserie[$c]['count'];
      echo $chartserie[$c]['data'];
      if($c<count($chartserie)-1)
         echo ",";
   }
?>], {
       title:'<?=addslashes($chart['title'])?>',
       legend: {
         show: <?=$chart['legend_show']?>,
         location:'<?=$chart['legend_position']?>',
         renderOptions: {
            placement: "<?=$chart['legend_placement']?>"
         }
       },
       grid: {
         shadow: <?=$chart['grid_shadow']?>,
         drawBorder: <?=$chart['grid_border']?>,
         background: '<?=$chart['grid_background']?>'
       },
       axes:{
             xaxis: {
                     renderer:$.jqplot.DateAxisRenderer,
                     tickRenderer:$.jqplot.CanvasAxisTickRenderer,
                     autoscale:true,
<?if($chart['x_numberTicks']) {
   if($maxseriecount<intval($chart['x_numberTicks'])) {?>
                     numberTicks: <?=$maxseriecount?>,
<? }else{?>
                     numberTicks: <?=$chart['x_numberTicks']?>,
<? }?>
<?}?>
                     tickOptions:{
<?if($chart['x_formatString']) {?>
                        formatString: <?=$chart['x_formatString']?>,
<?}?>
                        angle:30
                     }
             },
             yaxis: {
                min:0,
<?if($chart['y_numberTicks']) {?>
                     numberTicks: <?=$chart['y_numberTicks']?>,
<?}?>
                tickOptions:{
<?if($chart['y_formatString']) {?>
                   formatString: <?=$chart['y_formatString']?>
<?} else {?>
                   formatString:'%.<?=$chart['y_label_precision']?>f'
<?}?>
                }
             }
       },
       highlighter: {
         show: true,
         sizeAdjust: 7.5
       },
       cursor: {
         show: false
       },
       series:[
       <?
       for($c=0;$c<count($chartserie);$c++)
       {
         $serie=$chartserie[$c]['serie']
         ?>
         {
            label: '<?=addslashes($serie['label'])?>',
            lineWidth:<?=$serie['line_width']?>, 
            markerOptions:{
               style:'<?=$serie['marker_style']?>',
                  size: <?=$serie['marker_size']?>,
            },
            color:'<?=$serie['color']?>',
            showMarker: <?=$serie['marker_show']?>,
            showLine: true,
            fill: <?=$serie['fill']?>,
            fillAndStroke: true,
            highlighter: {
               formatString:'<?=$serie['highlighter_formatString']?>'
            }

         }<?
            if($c<count($chartserie)-1)
               echo ",\n";
      }
      ?>
       ],
       seriesDefaults:{
         rendererOptions: {
            smooth: true,
            shadowAlpha: 0.1,
            fillToZero: true
         }
       }
    });
<?
}
?>
});
</script>
