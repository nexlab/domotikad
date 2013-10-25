    <!-- JavaScript plugins (requires jQuery) -->
    <script src="/resources/js/jquery-1.9.0.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/resources/bootstrap/js/bootstrap.min.js"></script>
    <!-- Optionally enable responsive features in IE8 -->
    <script src="/resources/js/respond.min.js"></script>
    <!-- bootstrap switch --> 
    <script src="/resources/bootstrap-switch/static/js/bootstrap-switch.min.yui.js"></script>
    <script type="text/javascript">

   var es = new EventSource("/sse");

   var setDaemonStatus = function(event) {
      var data=$.parseJSON(event.data);
      if(data.data=='boardsdetection')
      {
         $("#modal_fixed").load('/resources/modals/autodetection_run.html');
         $("#modal_fixed").modal('show');
      } else if(data.data=='normal') {
         $("#modal_fixed").modal('hide');
         $("#modal_fixed").empty();
         location.reload();
      }

   }

   es.addEventListener("daemonstatus", setDaemonStatus);

   es.onerror = function(event){
     if(es.readystate=='CLOSED')
        es = new EventSource("/sse");
   }


   $.get("/rest/v1.2/daemonstatus/json",
      function(r){
         if(r.data=='boardsdetection')
         {
            $("#modal_fixed").load('/resources/modals/autodetection_run.html');
            $("#modal_fixed").modal('show');
         }
      }
   );

   setInterval(function(i){
      $.get("/rest/v1.2/keepalive/json", 
         function(r){
            if(r.data=='SLOGGEDOUT')
            {
               location.reload();
            }
            if($("#modal_offline").attr('aria-hidden')=='false')
               $("#modal_offline").modal('hide');
         }).fail(function(r){
            $("#modal_offline").modal('show');
         }
      );
   },5000);

   </script>
