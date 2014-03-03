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

function changeClimaStatus(newstatus, request){
   $("[data-domotika-type=btn-choosestatuses]").each(
      function(){
         $(this).html("<b>"+newstatus+'<b> <i class="glyphicon glyphicon-chevron-down"></i>')
      }
   );
   $("[data-domotika-type=statusselect]").each(
      function(){
         if($(this).attr('data-domotika-statusselect')==newstatus)
            $(this).hide();
         else
            $(this).show();
      }
   );
   if(typeof(request)!='undefined') {
      console.debug("Change status to "+newstatus);
      $.post("/rest/v1.2/clima/status/json", 'status='+newstatus);
   }
}

function changeThermostatStatus(newstatus, parts2, parts3, nopost)
{
   var program=$("#thermo-btnprogram-"+parts2+'-'+parts3);
   var manual=$("#thermo-btnmanual-"+parts2+'-'+parts3);
   var slide=$("#thermo-level-"+parts2+'-'+parts3);
   if(typeof(nopost)=='undefined')
      nopost=false;
   if(newstatus=='manual'){
      program.alterClass(program.attr('data-dmcolor-on'), program.attr('data-dmcolor-off'));
      manual.alterClass(manual.attr('data-dmcolor-off'), manual.attr('data-dmcolor-on'));
      if(!nopost)
         $.post("/rest/v1.2/clima/thermostat/"+manual.attr('data-domotika-thermostat')+"/json", 'function=manual&set='+slide.val().toString());
   } else {
      program.alterClass(program.attr('data-dmcolor-off'), program.attr('data-dmcolor-on'));
      manual.alterClass(manual.attr('data-dmcolor-on'), manual.attr('data-dmcolor-off'));
      if(!nopost)
         $.post("/rest/v1.2/clima/thermostat/"+manual.attr('data-domotika-thermostat')+"/json", 'function=program');
   }
}

function checkSliderSet(slider){
   if(slider.data('lastchanged'))
   {
      if(Date.now()-slider.data('lastchanged')>1000)
      {
         slider.data('lastchanged', false);
         var parts=slider.attr('id').split('-');  
         changeThermostatStatus('manual', parts[2], parts[3]);

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
               }
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
         }
      });

      var plus=$('#'+$(this).attr('id').replace('thermo-level-','thermo-plus-'));
      var minus=$('#'+$(this).attr('id').replace('thermo-level-','thermo-minus-'));

      minus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-minus-','thermo-level-'));
         slide.val(parseFloat(slide.val())-0.5);
         $('#'+$(this).attr('id').replace('thermo-minus-','thermo-showset-')).text(parseFloat(slide.val()).toFixed(1));
      }, 200, 700, true);

      plus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-plus-','thermo-level-'));
         slide.val(parseFloat(slide.val())+0.5);
         $('#'+$(this).attr('id').replace('thermo-plus-','thermo-showset-')).text(parseFloat(slide.val()).toFixed(1));
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
         var newstatus=$(this).attr('data-domotika-statusselect');
         changeClimaStatus(newstatus, true);
      });
   }
);

$("[data-domotika-type=btnprogram]").each(
   function(){$(this).fastClick(
      function() {
         var parts=$(this).attr('id').split("-");
         var other=$("#thermo-btnmanual-"+parts[2]+'-'+parts[3]);
         changeThermostatStatus('program', parts[2], parts[3]);
      });
   }
);

$("[data-domotika-type=btnmanual]").each(
   function(){$(this).fastClick(
      function() {
         var parts=$(this).attr('id').split("-");
         changeThermostatStatus('manual', parts[2], parts[3]);
      });
   }
);

var thermostatEvent = function(event) {
   var data=$.parseJSON(event.data);
   console.debug(data);
   if(typeof(data.data.action) != 'undefined'){
      var action=data.data.action;
      if(action=='climastatus'){
         changeClimaStatus(data.data.status);        
      }else if(action=='function'){
         $("[data-domotika-thermostat="+jQueryEscapesel(data.data.thermostat)+"][data-domotika-type=btnprogram]").each(
            function(){
               var parts=$(this).attr('id').split("-");
               changeThermostatStatus(data.data.func, parts[2], parts[3], true);
            }
         );
      }else if(action=='setval'){
         $("[data-domotika-thermostat="+jQueryEscapesel(data.data.thermostat)+"][data-domotika-type=btnprogram]").each(
            function(){
               var parts=$(this).attr('id').split("-");
               var slide=$("#thermo-level-"+parts[2]+'-'+parts[3]);              
               slide.val(parseFloat(data.data.val));
               slider.data('oldval', slider.val());
               $('#thermo-showset-'+parts[2]+'-'+parts[3]).text(parseFloat(data.data.val).toFixed(1));
            }
         );
      }
   }
}

es.addEventListener("thermostat", thermostatEvent);

</script>

