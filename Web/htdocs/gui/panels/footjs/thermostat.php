<? @include_once("../../includes/common.php"); ?>
<script>
$("[data-domotika-type=thermo-level]").each(
   function(){
      $(this).noUiSlider({
         range: [-10, 50],
         start: 20,
         handles: 1,
         connect: 'lower',
         orientation: 'vertical',
         direction: 'rtl',
         step:0.1,
         slide: function() {
                  var parts=$(this).attr('id').split("-");
                  $("#thermo-showset-"+parts[2]+'-'+parts[3]).text(parseFloat($(this).val()).toFixed(1));
               },
      });
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
         }
      });

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


</script>

