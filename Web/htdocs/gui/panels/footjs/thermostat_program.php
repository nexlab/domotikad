<? @include_once("../../includes/common.php"); ?>
<script>

function loadThermoProgs(parts2, parts3){
   $('#thermo-reset-'+parts2+'-'+parts3).prop('disabled', true);
   $('#thermo-save-'+parts2+'-'+parts3).prop('disabled', true);
   var climastatus=$("#thermo-btnstatus-"+parts2+'-'+parts3).attr("data-domotika-actualstatus");
   var thermoname=$('#thermo-reset-'+parts2+'-'+parts3).attr('data-domotika-thermostat');
   console.debug('loadThermoProgs '+thermoname+' '+climastatus);
   $.get("/rest/v1.2/clima/program/"+thermoname+"/"+climastatus+"/json", function(r){
         for(i=0;i<r.data.length;i++){
            d=r.data[i];
            var slidesel="[data-domotika-level-statusname="+jQueryEscapesel(climastatus)+"]";
            slidesel+="[data-domotika-level-thermoname="+jQueryEscapesel(thermoname)+"]";
            slidesel+="[data-domotika-level-day="+d.day+"]";
            $(slidesel).each(
               function(){
                  $(this).val(d[$(this).attr('data-domotika-level-hour')]);
               }  
            );
         }
      }
   );

}

function changeProgClimaStatus(newstatus, parts2, parts3){
   $("#thermo-btnstatus-"+parts2+"-"+parts3).each(
      function(){
         $(this).html("<b>"+newstatus+'<b> <i class="glyphicon glyphicon-chevron-down"></i>')
         $(this).attr("data-domotika-actualstatus", newstatus);
      }
   );
   var thermoname=$("#thermo-btnstatus-"+parts2+"-"+parts3).attr('data-domotika-btnthermoname');
   $("[data-domotika-level-thermoname="+jQueryEscapesel(thermoname)+"]").each(
      function(){
         $(this).attr('data-domotika-level-statusname', newstatus);
      }
   );
   $("[data-domotika-type=statuschoose]").each(
      function(){
         if($(this).attr('data-domotika-statuschoose')==newstatus)
            $(this).hide();
         else
            $(this).show();
      }
   );
   loadThermoProgs(parts2, parts3);
}

$("[data-domotika-type=thermoprogram]").each(
   function(){
      $(this).noUiSlider({
         range: [parseFloat($(this).attr('data-domotika-thermo-minslide')), parseFloat($(this).attr('data-domotika-thermo-maxslide'))],
         start: $(this).attr('data-domotika-thermo-startvalue'),
         handles: 1,
         direction: 'rtl',
         step:0.1,
         orientation: 'vertical',
         slide: function() {
                  var parts=$(this).attr('id').split("-");
                  $('#thermo-reset-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
                  $('#thermo-save-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
                  $('#'+$(this).attr('id').replace('thermo-levels-','thermo-values-')).text(parseFloat($(this).val()).toFixed(1));
               },
      });

      $(this).mousewheel(function(event) {
         if(event.deltaY>0)
            $(this).val(parseFloat($(this).val())+0.5);
         else if(event.deltaY<0)
            $(this).val(parseFloat($(this).val())-0.5);
         if(event.deltaY!=0)
         {
            $('#'+$(this).attr('id').replace('thermo-levels-','thermo-values-')).text(parseFloat($(this).val()).toFixed(1));
            var parts=$(this).attr('id').split("-");
            $('#thermo-reset-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
            $('#thermo-save-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
         }
      });

      var plus=$('#'+$(this).attr('id').replace('thermo-levels-','thermo-plus-'));
      var minus=$('#'+$(this).attr('id').replace('thermo-levels-','thermo-minus-'));

      minus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-minus-','thermo-levels-'));
         slide.val(parseFloat(slide.val())-0.5);
         $('#'+$(this).attr('id').replace('thermo-minus-','thermo-values-')).text(parseFloat(slide.val()).toFixed(1));
         var parts=$(this).attr('id').split("-");
         $('#thermo-reset-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
         $('#thermo-save-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
      }, 200, 1000, true);

      plus.continouoshold(function(){
         var slide=$('#'+$(this).attr('id').replace('thermo-plus-','thermo-levels-'));
         slide.val(parseFloat(slide.val())+0.5);
         $('#'+$(this).attr('id').replace('thermo-plus-','thermo-values-')).text(parseFloat(slide.val()).toFixed(1));
         var parts=$(this).attr('id').split("-");
         $('#thermo-reset-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
         $('#thermo-save-'+parts[2]+'-'+parts[3]).removeAttr('disabled');
      }, 200, 1000, true);
   }
);

$("[data-domotika-type=btn-statuses]").each(
   function() {
      $(this).fastClick(function(){
         var parts=$(this).attr('id').split("-");
         var panel="#thermo-statuslist-"+parts[2]+"-"+parts[3];
         if($(panel).css('display')=='block')
         {
            $(panel).hide(150);
         } else {
            $(panel).show(300);
         }
      });
   }
);

$("[data-domotika-type=statuschoose]").each(
   function(){
      $(this).fastClick(function(){
         var panel="#"+$(this).attr('data-domotika-panel');
         $(panel).hide(150);
         var newstatus=$(this).attr('data-domotika-statuschoose');
         var parts=$(this).attr('data-domotika-panel').split("-");
         changeProgClimaStatus(newstatus, parts[2], parts[3]);
      });
   }
);

$("[data-domotika-type=thermo-save]").each(
   function(){
      $(this).on('click', function(){
         var parts=$(this).attr('id').split("-");
         $(this).prop('disabled', true);
         $('#thermo-reset-'+parts[2]+'-'+parts[3]).prop('disabled', true);
         var climastatus=$("#thermo-btnstatus-"+parts[2]+'-'+parts[3]).attr("data-domotika-actualstatus");
         var thermoname=$('#thermo-reset-'+parts[2]+'-'+parts[3]).attr('data-domotika-thermostat');
         var slidesel="[data-domotika-level-statusname="+jQueryEscapesel(climastatus)+"]";
         slidesel+="[data-domotika-level-thermoname="+jQueryEscapesel(thermoname)+"]";
         var postdata={'thermoname': thermoname, 'climastatus': climastatus, 
                        'mon':{},'tue':{},'wed':{},'thu':{},'fri':{},'sat':{},'sun':{}
                      };
         $(slidesel).each(
            function(){
               var day=$(this).attr('data-domotika-level-day');
               var hour=$(this).attr('data-domotika-level-hour');
               postdata[day][hour]=parseFloat($(this).val());
            }
         );
         $.ajax({
            type:'POST',
            url:"/rest/v1.2/clima/program/"+thermoname+"/"+climastatus+"/json",
            contentType:"application/json; charset=utf-8",
            data: JSON.stringify(postdata),
            dataType:"json",
            success: function(r){
               console.debug('thermostat program saved');
            }
         });
      });
   }
);

$("[data-domotika-type=thermo-reset]").each(
   function(){
      $(this).on('click', function(){
         var parts=$(this).attr('id').split("-");
         loadThermoProgs(parts[2], parts[3]);
      });
   }
);


$('a[data-toggle="tab"]').on('shown.bs.tab',function(){
   $(window).trigger('resize');
});

$(function () {
    $('.thermotab a:first').tab('show');
});

var thermoProgramEvent = function(event) {
   var data=$.parseJSON(event.data);
   console.debug(data);
   if(typeof(data.data.action) != 'undefined'){
      var action=data.data.action;
      if(action=='updated'){
         var thermostat=data.data.thermostat;
         var climastatus=data.data.climastatus;
         jsel="[data-domotika-actualstatus="+jQueryEscapesel(climastatus)+"]";
         jsel+="[data-domotika-btnthermoname="+jQueryEscapesel(thermostat)+"]";
         $(jsel).each(
            function(){
               var parts=$(this).attr('id').split('-')
                  loadThermoProgs(parts[2], parts[3]);
            }
         );
      }
   }
}

es.addEventListener("thermoprogram", thermoProgramEvent);

</script>
