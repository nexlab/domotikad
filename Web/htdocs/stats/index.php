<?
include_once("common_includes.php");
include_once("include.php");
?>
<html>
<head title="Domotika GUI stats">
   <title>Domotika GUI Stats</title>
   <meta charset="utf-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
   <meta content="true" name="HandheldFriendly" />
   <meta content="320" name="MobileOptimized" /> 
   <meta name="apple-mobile-web-app-capable" content="yes">
   <meta name="apple-mobile-web-app-status-bar-style" content="black">
   <meta http-equiv="cleartype" content="on">
   <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
   <script src="/resources/js/jquery-1.9.0.min.js" type="text/javascript" ></script>
   <script src="/resources/js/jquery-migrate-1.0.0.min.js" type="text/javascript" ></script>
   <script src="/resources/js/sockjs-0.3.min.js" ></script>
   <script src="/resources/js/ajaxsocket.js" ></script>
   <!--[if lt IE 9]><script language="javascript" type="text/javascript" src="/resources/js/jqplot/excanvas.min.js"></script><![endif]-->
   <script src="/resources/js/jqplot/jquery.jqplot.min.js" ></script>
   <link rel="stylesheet" type="text/css" href="/resources/js/jqplot/jquery.jqplot.min.css" />
   <script type="text/javascript" src="/resources/js/jqplot/plugins/jqplot.dateAxisRenderer.min.js"></script>
   <script type="text/javascript" src="/resources/js/jqplot/plugins/jqplot.highlighter.min.js"></script>
   <script type="text/javascript" src="/resources/js/jqplot/plugins/jqplot.cursor.min.js"></script>
   <script type="text/javascript" src="/resources/js/jqplot/plugins/jqplot.canvasTextRenderer.min.js"></script>
   <script type="text/javascript" src="/resources/js/jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js"></script>
   <style>
   </style>
</head>
<body>
<?
$days = getLastNDays(7, 'Y-m-d' );
$daysql = getLastNDays(7, 'Y-m-d');
$charts=DB::query("SELECT * FROM stats_charts WHERE active=1 order by webposition");

?>
<h1>Statistiche impianto domotico</h1>
<h2>Tutti i grafici</h2>
<?
foreach($charts as $chart)
{?>
<hr/>
<div id="<?=$chart['name']?>" style="height:250px;width:700px"></div>
<?}?>
<script type="text/javascript">
$(document).ready(function() {
<?
foreach($charts as $chart)
{
   $chartserie = getChartData($chart['name']);
?>

var plot_<?=$chart['name']?>=$.jqplot('<?=$chart['name']?>', [<?
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
window.setTimeout('location.reload()', 60000);

});

</script>
</body>
</html>
