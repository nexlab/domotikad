<? @include_once("../../includes/common.php"); ?>

<script>

function thermoResetGaugeLevel(g,l) {
   var gau=gaugeArray[g];
   gau.config.customSectors[2]={color: gau.config.customSectors[2].color,
                                  lo: gau.config.customSectors[2].lo,
                                  hi: l}
   gau.config.customSectors[3]={color: gau.config.customSectors[3].color,
                                  lo: l,
                                  hi: gau.config.customSectors[3].hi};
   gau.refresh(gau.config.value);

}

function checkSliderSet(slider){
   if(slider.data('lastchanged'))
   {
      if(Date.now()-slider.data('lastchanged')>1000)
      {
         console.debug(slider.data('lastchanged'));
         console.debug(Date.now());  
         console.debug('------------------------');
         slider.data('lastchanged', false);
      }
   }
   if(slider.val()!=slider.data('oldval'))
   {
      slider.data('lastchanged', Date.now());
      slider.data('oldval', slider.val());
   }
   setTimeout(function(){checkSliderSet(slider)}, 500);
}

$("[data-domotika-type=thermo-level]").each(
   function(){
      $(this).noUiSlider({
         range: [parseFloat($(this).attr('data-domotika-minval')), parseFloat($(this).attr('data-domotika-maxval'))],
         start: parseFloat($(this).attr('data-domotika-setval')),
         handles: 1,
         connect: 'lower',
         orientation: 'vertical',
         direction: 'rtl',
         step:0.1,
         slide: function() {
                  var parts=$(this).attr('id').split("-");
                  $("#thermo-showset-"+parts[2]+'-'+parts[3]).text(parseFloat($(this).val()).toFixed(1));
                  thermoResetGaugeLevel('gauge-'+parts[2]+'-'+parts[3], parseFloat($(this).val()));
                  var program=$("#thermo-btnprogram-"+parts[2]+'-'+parts[3]);
                  var manual=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
                  program.alterClass(program.attr('data-dmcolor-on'), program.attr('data-dmcolor-off'));
                  manual.alterClass(manual.attr('data-dmcolor-off'), manual.attr('data-dmcolor-on'));
               },
         /*
         set: function() {
                  $(this).data('lastchanged', Date.now());
               }
         */
      });
      $(this).data('oldval', $(this).val());
      $(this).data('lastchanged', false);
      slider=$(this);
      setTimeout(function(){checkSliderSet(slider)}, 1000);

      var parts=$(this).attr('id').split('-');
      var btn=$("#thermo-showset-"+parts[2]+'-'+parts[3]);
      btn.text(parseFloat($(this).val()).toFixed(1));

      $(this).mousewheel(function(event) {
         if(event.deltaY>0)
            $(this).val(parseFloat($(this).val())+0.5);
         else if(event.deltaY<0)
            $(this).val(parseFloat($(this).val())-0.5);
         if(event.deltaY!=0)
         {
            $('#'+$(this).attr('id').replace('thermo-level-','thermo-showset-')).text(parseFloat($(this).val()).toFixed(1));
            thermoResetGaugeLevel('gauge-'+parts[2]+'-'+parts[3], parseFloat($(this).val()));
            var program=$("#thermo-btnprogram-"+parts[2]+'-'+parts[3]);
            var manual=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
            program.alterClass(program.attr('data-dmcolor-on'), program.attr('data-dmcolor-off'));
            manual.alterClass(manual.attr('data-dmcolor-off'), manual.attr('data-dmcolor-on'));
            //$(this).data('lastchanged', Date.now());
         }
      });

      var plus=$('#'+$(this).attr('id').replace('thermo-level-','thermo-plus-'));
      var minus=$('#'+$(this).attr('id').replace('thermo-level-','thermo-minus-'));

      minus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-minus-','thermo-level-'));
         slide.val(parseFloat(slide.val())-0.5);
         $('#'+$(this).attr('id').replace('thermo-minus-','thermo-showset-')).text(parseFloat(slide.val()).toFixed(1));
         var parts=$(this).attr('id').split("-");
         var program=$("#thermo-btnprogram-"+parts[2]+'-'+parts[3]);
         var manual=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
         program.alterClass(program.attr('data-dmcolor-on'), program.attr('data-dmcolor-off'));
         manual.alterClass(manual.attr('data-dmcolor-off'), manual.attr('data-dmcolor-on'));
         //slide.data('lastchanged', Date.now());
      }, 200, 700, true);

      plus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-plus-','thermo-level-'));
         slide.val(parseFloat(slide.val())+0.5);
         $('#'+$(this).attr('id').replace('thermo-plus-','thermo-showset-')).text(parseFloat(slide.val()).toFixed(1));
         var parts=$(this).attr('id').split("-");
         var program=$("#thermo-btnprogram-"+parts[2]+'-'+parts[3]);
         var manual=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
         program.alterClass(program.attr('data-dmcolor-on'), program.attr('data-dmcolor-off'));
         manual.alterClass(manual.attr('data-dmcolor-off'), manual.attr('data-dmcolor-on'));
         //slide.data('lastchanged', Date.now());
      }, 200, 700, true);

   }
);

$("[data-domotika-type=btn-choosestatuses]").each(
   function() {
      $(this).fastClick(function(){
         var parts=$(this).attr('id').split("-");
         var panel="#thermo-statuschooselist-"+parts[2]+"-"+parts[3];
         if($(panel).css('display')=='block')
         {
            $(panel).hide(150);
         } else {
            $(panel).show(300);
         }
      });
   }
);

$("[data-domotika-type=statusselect]").each(
   function(){
      $(this).fastClick(function(){
         var panel="#"+$(this).attr('data-domotika-panel');
         $(panel).hide(150);
      });
   }
);

$("[data-domotika-type=btnprogram]").each(
   function(){$(this).fastClick(
      function() {
         var parts=$(this).attr('id').split("-");
         var other=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
         other.alterClass(other.attr('data-dmcolor-on'), other.attr('data-dmcolor-off'));
         $(this).alterClass($(this).attr('data-dmcolor-off'), $(this).attr('data-dmcolor-on'));
      });
   }
);

$("[data-domotika-type=btnmanual]").each(
   function(){$(this).fastClick(
      function() {
         var parts=$(this).attr('id').split("-");
         var other=$("#thermo-btnprogram-"+parts[2]+'-'+parts[3]);
         other.alterClass(other.attr('data-dmcolor-on'), other.attr('data-dmcolor-off'));
         $(this).alterClass($(this).attr('data-dmcolor-off'), $(this).attr('data-dmcolor-on'));
      });
   }
);

</script>

