<? @include_once("../../includes/common.php"); ?>
<script>
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
      });
   }
);

$("[data-domotika-type=thermo-save]").each(
   function(){
      $(this).on('click', function(){
         var parts=$(this).attr('id').split("-");
         $(this).prop('disabled', true);
         $('#thermo-reset-'+parts[2]+'-'+parts[3]).prop('disabled', true);
      });
   }
);

$("[data-domotika-type=thermo-reset]").each(
   function(){
      $(this).on('click', function(){
         var parts=$(this).attr('id').split("-");
         $(this).prop('disabled', true);
         $('#thermo-save-'+parts[2]+'-'+parts[3]).prop('disabled', true);
      });
   }
);


$('a[data-toggle="tab"]').on('shown.bs.tab',function(){
   $(window).trigger('resize');
});

$(function () {
    $('.thermotab a:first').tab('show');
});

</script>
