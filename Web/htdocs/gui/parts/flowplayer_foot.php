<script src="/resources/flowplayer/flowplayer.min.js"></script>
<script>
$('.flowplayer video').each(
   function() {
      //$(this).attr('duration', 0);
      console.debug($(this));
   }
);
/*
$('.flowplayer video').on('timeupdate',
   function() {
     // $(this).attr('duration', 0);
     console.debug($(this));
   }
);
*/

$('.flowplayer').on('ready',
   function() {
      //$(this).attr('duration', 0);
      console.debug($(this));
   }
);
flowplayer(function (api, root) {
   api.bind("ready", function (e, api, video) {
      console.debug(video.duration);
      
      
      //if(typeof video.duration == "undefined" || video.duration =="Infinity")
      //   video.duration=0;
   });
   api.bind("error", function (e, api, video) {
      console.debug("error");
   });
}); 

</script>
