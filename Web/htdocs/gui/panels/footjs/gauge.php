<? @include_once("../../includes/common.php"); ?>
<script>

function gaugeFloat(fval)
{
   return fval;
}

var gaugeArray = new Array();
$("[data-domotika-type=gauge]").each(
   function (){
      if($(this).attr('data-dmval-min')!=$(this).attr('data-dmval-low') && $(this).attr('data-dmval-min')!=$(this).attr('data-dmval-high'))
      {
         var customS=[
            {color: stringColors[$(this).attr('data-dmcolor-min')], 
               lo: $(this).attr('data-dmval-min')/$(this).attr('data-dmval-divider'), 
               hi: $(this).attr('data-dmval-low')/$(this).attr('data-dmval-divider')},
            {color: stringColors[$(this).attr('data-dmcolor-low')], 
               lo: $(this).attr('data-dmval-low')/$(this).attr('data-dmval-divider'), 
               hi: (($(this).attr('data-dmval-low')/$(this).attr('data-dmval-divider'))
                     +((($(this).attr('data-dmval-high')-$(this).attr('data-dmval-low'))/2)/$(this).attr('data-dmval-divider')))},
            {color: stringColors[$(this).attr('data-dmcolor-medium')], 
               lo: (($(this).attr('data-dmval-low')/$(this).attr('data-dmval-divider'))
                     +((($(this).attr('data-dmval-high')-$(this).attr('data-dmval-low'))/2)/$(this).attr('data-dmval-divider'))), 
               hi: $(this).attr('data-dmval-high')/$(this).attr('data-dmval-divider')},
            {color: stringColors[$(this).attr('data-dmcolor-high')], 
               lo: $(this).attr('data-dmval-high')/$(this).attr('data-dmval-divider'), 
               hi: $(this).attr('data-dmval-max')/$(this).attr('data-dmval-divider')}
         ];
         console.debug(customS);
      } else {
         var customS=false;
         var levelC=new Array(
               stringColors[$(this).attr('data-dmcolor-min')], 
               stringColors[$(this).attr('data-dmcolor-low')], 
               stringColors[$(this).attr('data-dmcolor-medium')], 
               stringColors[$(this).attr('data-dmcolor-high')]
            );
      }
      gaugeArray[$(this).attr('id')]=new JustGage({
                                          id:$(this).attr('id'),
                                          value: 0,
                                          textRenderer: gaugeFloat,
                                          min: $(this).attr('data-dmval-min')/$(this).attr('data-dmval-divider'),
                                          max: $(this).attr('data-dmval-max')/$(this).attr('data-dmval-divider'),
                                          valueFontColor: "#999999",
                                          title: $(this).attr('data-domotika-name'),
                                          labelFontColor: "#999999",
                                          label: $(this).attr('data-domotika-label'),
                                          customSectors: customS,
                                      });
       gaugeArray[$(this).attr('id')].refresh($(this).attr('data-dmval')/$(this).attr('data-dmval-divider'));
      $(this).data('gauge', gaugeArray[$(this).attr('id')]);
   }
);
</script>
