<? @include_once("../includes/common.php");?>
    <? /*
    <!-- JavaScript plugins (requires jQuery) -->
    <script src="/resources/js/jquery-1.9.0.min.js"></script>
    <script src="/resources/jquery-color/jquery.color.min.js"></script>
    <script src="/resources/hammer.js/dist/hammer.min.js"></script> 
    <script src="/resources/hammer.js/plugins/hammer.fakemultitouch.js"></script>
    <!--[if !IE]> -->
    <script>
      Hammer.plugins.fakeMultitouch();
   </script>
    <!-- <![endif]-->
    <script src="/resources/hammer.js/dist/jquery.hammer.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/resources/bootstrap/js/bootstrap.min.js"></script>
    <!-- Optionally enable responsive features in IE8 -->
    <script src="/resources/js/respond.min.js"></script>
    <!-- bootstrap switch -->
    <script src="/resources/bootstrap-switch/static/js/bootstrap-switch.min.yui.js"></script>
    <!-- Snap.js -->
    <script src="/resources/Snap.js/snap.min.js"></script>
    <!-- AppScroll.js -->
    <script src="/resources/AppScroll.js/AppScroll.min.js"></script>
    <!-- EventSource (aka Server-Sent Events) -->
    <script src="/resources/EventSource/eventsource.js"></script>
   */ ?>
   <script src="<?=$BASEGUIPATH;?>/js/combined.min.js"></script>
   <script>

   var ttsEnabled=<?=$_DOMOTIKA['tts']?>; 
  
   //var scroller = new AppScroll({
   //   toolbar: $('#topbar')[0],
   //   scroller: $('#content')[0]
   //})

   var audioTagSupport = !!(document.createElement('audio').canPlayType);
      
   function tmpPopover(el, cont, placement, timeout)
   {
      el.popover({
         placement: placement,
         content: cont,
         delay: {show: 100, hide: timeout},
         trigger: "manual"});
      el.popover("show");
      setTimeout(function(){el.popover("destroy")}, timeout);
   }

   function playTTS(text, lang, force)
   {
      if(typeof(force)==='undefined') force=false;
      if(typeof(lang)==='undefined') lang = "it";
      if (!audioTagSupport) return false;
      if (text=='') return false;
      if (ttsEnabled!=1 && force===false) return false;
      var audio = document.createElement('audio');
      // XXX BUG: webkit based browsers seems to not work with https:// in <audio>, so, we fix this to http
      audio.setAttribute('src', 'http://translate.google.com/translate_tts?tl='+lang+'&q=' + encodeURIComponent(text));
      audio.load();
      audio.play();
   }  

   function speechResult(data) {
      if(data.result=='succeed')
      {
         var resp=data.data[0];
         if(resp=='NOACT')
            resp="Nessuna corrispondenza";
         tmpPopover($("#speech"), resp, 'top', 1500);
         playTTS(resp);
      }
   }

   function sendSpeech(spobj)
   {
      $.post("/rest/v1.2/actions/speech_text/json", spobj.serialize(), speechResult );
   }

   var popupFader = function(ftype, title, message, timeout){
      if(typeof(timeout)==='undefined') timeout = 1500;
      $("#alertTitle").text(title);
      $("#alertMessage").text(" "+message);
      $("#alertPopup").removeClass();
      $("#alertPopup").addClass("alert alert-"+ftype);
      $("#alertContainer").fadeIn(100);
      $("#alertContainer").fadeOut({duration:timeout, easing:'easeInQuint'});
   };

   <? if($left || $right) { ?>
   var snapper = new Snap({
      resistance: 0,
      easing: 'linear',
      transitionSpeed: 0.1,
      tapToClose: false,
      element: $('#content')[0],
      //dragger: $('#content')[0],
      dragger: $('[data-domotika-dragger="true"]')[0],
      minDragDistance: 20,
      slideIntent: 30
   });
   <? } ?>   

    <? if($left || $right) { ?>
   snapper.on('animating',
      function(e) {
         if($(window).width()>768)
            mval=Math.min(Math.ceil((75/100)*$(window).width()), 800);
         else
            mval=Math.max(Math.ceil((75/100)*$(window).width()), 266);
         <? if($left) { ?>
         if(snapper.state().info.opening=='left' && snapper.state().state!='left' && $(".left-drawer").css("width")!=mval+"px")
         {
            $(".left-drawer").css("width", mval);
            snapper.settings({maxPosition: mval,easing:'ease',transitionSpeed:0.3});
            snapper.on('animated', function(e){ 
               snapper.off('animated');
               snapper.open('left');
            }); 
                   
         }
         <? } ?>
         <? if($left && $right) { ?> else <? } ?><? if($right) { ?>if(snapper.state().info.opening=='right' && snapper.state().state!='right' && $(".right-drawer").css("width")!=mval+"px")
         {
            $(".right-drawer").css("width", mval)
            snapper.settings({minPosition: -mval,easing:'ease',transitionSpeed:0.3});
            snapper.on('animated', function(e){ 
               snapper.off('animated');
               snapper.open('right');
            }); 
         }
         <? } ?>
      });
   <? } ?>
   
    <? if($left) { ?>
   //$('#open-left').on('click', 
   $('#open-left').fastClick(
      function(e) {
         if(snapper.state().state=='left')
            snapper.close('left');
         else {
            snapper.open('left');
         }
         
      });
   <? } ?>
   <? if($right) { ?>
   //$('#open-right').on('click', 
   $('#open-right').fastClick(
      function(e) {
         if(snapper.state().state=='right')
            snapper.close('right');
         else {
            snapper.open('right');
         }
      });
   <? } ?>

   function notifylistitem(text, source, nid, ndate)
   {
      var nd = new Date(parseInt(ndate*1000));
      var ndate=nd.toLocaleString();
      var nli='<?=notifyListItem();?>';
      nli=nli.replace('[TXT]', text);
      nli=nli.replace('[NDATE]', ndate);
      nli=nli.replace('[NSOURCE]', source);
      nli=nli.replace('[NID]', nid);
      return nli;
   }


   //$("#notifybutton").on('click',
   $("#notifybutton").fastClick(
      function(e) {
         if($("#notifypanel").is(":hidden")) {
            var hval=Math.ceil((75/100)*$(window).height());
            var wval=Math.min(Math.ceil((75/100)*$(window).width()), 500);
            $("#notifypanel").css("height", hval);
            $("#notifypanel").css("width", wval);
            $(".notifylist").css("height", hval-78);
            $("#notifications").empty();
            $.get("/rest/v1.2/notifications/json", function(r){
            for(i=0;i<r.data.length;i++)
            {
               $("#notifications").prepend(notifylistitem(r.data[i].message, r.data[i].source, r.data[i].id, r.data[i].added));     
            }
         });

      }
      $.get("/rest/v1.2/notifications/count/json", function(r){ $("#notifybadge").text(r.data);});
      $("#notifypanel").slideToggle(200);
   });

   $('#speech').bind('webkitspeechchange',function(event) {
      event.preventDefault();
      sendSpeech($("#speech"));
   });

   $('#speechsm').bind('webkitspeechchange',function(event) {
      event.preventDefault();
      sendSpeech($("#speech"));
   });

   $("#speech").keypress(function(event) {
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if(keycode == 13) {
         event.preventDefault();
         sendSpeech($("#speech"));
      }
   });

   $("#speechsm").keypress(function(event) {
      var keycode = (event.keyCode ? event.keyCode : event.which);
      if(keycode == 13) {
         event.preventDefault();
         sendSpeech($("#speechsm"));
      }
   });

   var es = new EventSource("/sse");

   var syncReceived = function(event) {
      var res=$.parseJSON(event.data);
      $.each(res.data.statuses, function(idx, val){
         console.debug(val);
         switch(val[3])
         {
            case 'relay':
               var sel="data-domotika-relid";
               $("[data-domotika-ampid="+val[0]+"]").each(
                  function() {
                     $(this).text(val[2]/10);
                  }
               ); 
               $("[data-domotika-ampcol="+val[0]+"]").each(
                  function() {
                     var ampere=val[2]/10;
                     if(ampere>0 && ampere<8) {
                        var badgecolor="badge-success";
                     }else if(ampere>=8 && ampere<11) {
                        var badgecolor="badge-info";
                     }else if(ampere>=11 && ampere<14) {
                        var badgecolor="badge-warning";
                     }else if(ampere>=14) {
                        var badgecolor="badge-danger";
                     } else {
                        var badgecolor="";
                     }
                     $(this).alterClass("badge-*", badgecolor);
                  }
               ); 
               break;
            case 'input':
               var sel="data-domotika-inpid";
               $("[data-domotika-inpled="+val[0]+"]").each(
                  function() {
                     if(val[1]>0) {
                        $(this).alterClass($(this).attr('data-dmcolor-off'), $(this).attr('data-dmcolor-on'));   
                     } else {
                        $(this).alterClass($(this).attr('data-dmcolor-on'), $(this).attr('data-dmcolor-off'));
                     }
                  }
               );
               break;
            case 'analog':
               $("[data-domotika-analed="+val[0]+"]").each(
                  function() {
                    console.debug("analed");
                  }
               );
               $("[data-domotika-anaid="+val[0]+"]").each(
                  function() {
                    console.debug("anaid");
                  }
               );

               break;
            case 'action':
               var sel="data-domotika-actid";
               $("[data-domotika-act2textid="+val[0]+"]").each(
                  function() {
                     if(val[2]>0) {
                        $(this).text($(this).attr('data-dmtext-on'));
                     } else {
                        $(this).text($(this).attr('data-dmtext-off'));
                     }
                  }
               );
               $("[data-domotika-act2col="+val[0]+"]").each(
                  function() {
                     if(val[2]>0) {
                        $(this).alterClass($(this).attr('data-dmcolor-off'), $(this).attr('data-dmcolor-on'));
                     } else {
                        $(this).alterClass($(this).attr('data-dmcolor-on'), $(this).attr('data-dmcolor-off'));
                     }
                  }
               );

               break;
         }
         if(val[3]!="analog") {
            $("["+sel+"="+val[0]+"]").each(
               function() {
                  if($(this).prop("nodeName")=="BUTTON") {
                     if(val[1]>0) {
                        $(this).alterClass($(this).attr('data-dmcolor-off'), $(this).attr('data-dmcolor-on'));
                        $(this).text($(this).attr('data-dmtext-on'));
                     } else {
                        $(this).alterClass($(this).attr('data-dmcolor-on'), $(this).attr('data-dmcolor-off'));
                        $(this).text($(this).attr('data-dmtext-off'));
                     }
                  } else if($(this).prop("nodeName")=="DIV" && $(this).hasClass('has-switch')) {
                     $(this).bootstrapSwitch('setState', val[1], true);
                  }
               }  
            );
         } // if !=analog
      });
   };

   var notificationReceived = function(event) {
      var data=$.parseJSON(event.data);
      var nt=data.data;
      var ts=data.ts
      $.get("/rest/v1.2/notifications/count/json", function(r){ $("#notifybadge").text(r.data);});
      tmpPopover($("#notifybutton"), "New Notify: "+nt.msg, 'left', 1000);     
      if($("#notifypanel").is(":visible"))
      {
         $("#notifications").prepend(notifylistitem(nt.msg, nt.source, nt.nid, ts));
         $("#notifyid-"+nt.nid).animate({backgroundColor: "#0080ff"},200);
         $("#notifyid-"+nt.nid).animate({backgroundColor: "#fff"},3500);
      }
      playTTS("nuova notifica,"+nt.msg);
      
   };

   var deleteNotification = function(el)
   {
      el.fadeOut(500, function(){el.remove();});
      $.ajax({url: "/rest/v1.2/notifications/"+el.attr('id').split("-")[1]+"/json", type:"DELETE", success: function(res){
         $.get("/rest/v1.2/notifications/count/json", function(r){ 
            $("#notifybadge").text(r.data);
            });
         }
      });
   }

   $("#notifications").hammer().on("swipeleft", ".notify-swipe-deletable", 
      function() {
         deleteNotification($(this));
      });
   $("#notifications").on("click", 'i.notify-deletable',
      function() {
         deleteNotification($(this).parent().parent());
      });
   $("#notify-removeall").on("click", 
      function(){
         $.ajax({url: "/rest/v1.2/notifications/", type:"DELETE", success:function(res){
            $("#notifypanel").slideToggle(200);
            $.get("/rest/v1.2/notifications/count/json",function(r){
               $("#notifybadge").text(r.data);
            });
         }});  
      });
   
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
   es.addEventListener("notify", notificationReceived);
   es.addEventListener("sync", syncReceived);

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

   $.get("/rest/v1.2/notifications/count/json", function(r){ $("#notifybadge").text(r.data);});

   </script>
