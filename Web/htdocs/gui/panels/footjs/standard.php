<script>
   $(".devlist-button").on("click",
      function(ev) {
         if($(this).is("[data-domotika-actid]"))
            $.post("/rest/v1.2/actions/setbyid/"+$(this).attr('data-domotika-actid')+"/json");
         else
            $.post("/rest/v1.2/relays/setbyid/"+$(this).attr('data-domotika-relid')+"/json");
      }); 

   $(".devlist-switch").on("switch-change",
      function(ev, data) {
         if(data.value)
            var cmd="on"
         else
            var cmd="off"
         if($(this).is("[data-domotika-actid]"))
            $.post("/rest/v1.2/actions/setbyid/"+$(this).attr('data-domotika-actid')+"/"+cmd+"/json");
         else
            $.post("/rest/v1.2/relays/setbyid/"+$(this).attr('data-domotika-relid')+"/"+cmd+"/json");
      }); 
</script>
