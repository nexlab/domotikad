<? @include_once("../../includes/common.php"); ?>
<?
$days = getLastNDays(7, 'Y-m-d' );
$daysql = getLastNDays(7, 'Y-m-d');

?>
<script type="text/javascript">

var ajaxCharts = [];
function plotGraph(settings)
{
   t = this;
   $.extend(t.settings, settings);
   $.ajax({
      async:false,
      url: t.settings.data_url,
      dataType: "json",
      success: function(res){  
         res.data.opt.axes.xaxis.renderer=$.jqplot.DateAxisRenderer;
         res.data.opt.axes.xaxis.tickRenderer=$.jqplot.CanvasAxisTickRenderer;
         //$("#"+t.settings.eid).empty();
         if(typeof(t.jq)!='undefined')
            t.jq.destroy();
         t.jq=$.jqplot(t.settings.eid, res.data.data, res.data.opt);
         //t.jq.destroy();
   
      }
   });
}
<?
foreach($_SESSION['PANELS_CHARTS'] as $eid => $chart)
{
?>

ajaxCharts[ajaxCharts.length] = {
   settings: {
      eid: "<?=$eid?>",
      data_url: "/rest/v1.2/charts/chartbyname/<?=$chart['name']?>/json"
   },
   
   plot: plotGraph
};

<?
}
?>
function chartsPlot()
{
   for(i=0;i<ajaxCharts.length;i++)
   {
      ajaxCharts[i].plot();
   }
}

$(window).load(function(){
   chartsPlot();
   setInterval(chartsPlot, 10000);
});
//$(".chartpanel").scrollLeft(10000);

</script>
