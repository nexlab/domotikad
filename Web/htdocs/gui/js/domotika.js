<? @include_once("../includes/common.php");?>
   //document.documentElement.requestFullscreen();

   //window.screen.mozLockOrientation('portrait');
   <?
      $baseg=str_replace("/js/domotika.js","",$BASEGUIPATH);
      $baseg=str_replace("/js/combined.min.js", "", $baseg);
   ?>

   var BASEGUIPATH='<?=$baseg?>';
   var sectar=window.location.pathname.replace(BASEGUIPATH, "").split("/");
   var GUISECTION="index";
   if(sectar.length>1 && sectar[1].length>0 && sectar[1]!='actuations')
      GUISECTION=sectar[1];
   var GUISUBSECTION="";
   if(sectar.length>2)
      GUISUBSECTION=sectar[2];
   console.debug(sectar);
   console.debug(GUISECTION);

   var windowWidth = window.screen.width < window.outerWidth ?
                  window.screen.width : window.outerWidth;
   var mobile = windowWidth < 500;

   var ttsEnabled=<?=$_DOMOTIKA['tts']?>; 
   var slideEnabled=<?=$_DOMOTIKA['slide']?>;
   var speechEnabled='<?=$_DOMOTIKA["webspeech"]?>';

   var notifyColor='#fff';
   if('<?=$_DOMOTIKA["gui_theme"]?>'=='dmblack')
      notifyColor='#000';

   var stringColors = {
      'red': '#ff0000',
      'green': '#5cb85c',
      'gray': '#999999',
      'orange': '#f0ad4e',
      'blue': '#428bca',
      'azure': '#5bc0de',
      'black': '#000000',
      'white': '#ffffff'
   };

   //var scroller = new AppScroll({
   //   toolbar: $('#topbar')[0],
   //   scroller: $('#content')[0]
   //})

   var audioTagSupport = !!(document.createElement('audio').canPlayType);
   /*  
   function DoFullScreen() {
      if (!document.fullscreenElement &&    // alternative standard method
            !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement ) {  // current working methods
         if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
         } else if (document.documentElement.msRequestFullscreen) {
            document.documentElement.msRequestFullscreen();
         } else if (document.documentElement.mozRequestFullScreen) {
            document.documentElement.mozRequestFullScreen();
         } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
         }
      }
   }
   */

   (function () {
      var previousScroll = 0;

      $(window).scroll(function(event){
         $(this).scrollLeft()!=0;
         $(window).scrollLeft(0);
         event.preventDefault();
      });
   }()); // to disable right scroll on panels open

   $(window).scroll(function(event){
      console.debug(event);
   });

   if(window.navigator.userAgent.match(/(iPad|iPhone|iPod)/g))
   {
      $(document).ready(function(){
         if (("standalone" in window.navigator) && window.navigator.standalone) {
            // For iOS Apps
            $('a').on('click', function(e){
               e.preventDefault();
               var new_location = $(this).attr('href');
               if (new_location != undefined && new_location.substr(0, 1) != '#' && $(this).attr('data-method') == undefined){
                  window.location = new_location;
               }
            });
         }
      });


   }


   if(window.navigator.userAgent.match(/firefox/i) && window.navigator.userAgent.match(/mobile/i))
   {

      var installbutton = $("#installbutton");
      var port="";
      if(document.location.port)
         var port=":"+document.location.port;
      <?
         $manif=str_replace("/js/domotika.js","",$BASEGUIPATH);
         $manif=str_replace("/js/combined.min.js", "", $manif);
      ?>
      var manifest_url = document.location.protocol+"//"+document.location.host+port+"<?=$manif?>/manifest.webapp";
         
      function installFFApp(ev) {
         ev.preventDefault();
         var myapp = navigator.mozApps.install(manifest_url);
         myapp.onsuccess = function(data) {
            $("#install_ff").hide()
            console.log(this);
            popupFader('success', 'SUCCESS:','Web app installata correttamente');
            var a = playTTS('Web app installata correttamente');

         };
         myapp.onerror = function() {
            console.log('Install failed, error: ' + this.error.name);
            popupFader('danger', 'ERROR:', 'App not installed: '+this.error.name);
            playTTS('Errore, applicazione non installata');
         };
      };
   

      var installCheck = navigator.mozApps.checkInstalled(manifest_url);

      installCheck.onsuccess = function() {
         if(installCheck.result) {
            $("#install_ff").hide();
         } else {
            $("#install_ff").show();
            installbutton.on('click', installFFApp);
         };
      };
   }

   if(mobile)
   {
      if(jQuery.isFunction(window.screen.lockOrientation))
         window.screen.lockOrientation('portrait');
      else if(jQuery.isFunction(window.screen.mozLockOrientation))
         window.screen.mozLockOrientation('portrait');
      else if(jQuery.isFunction(window.screen.msLockOrientation))
         window.screen.msLockOrientation('portrait');
      else if(jQuery.isFunction(window.screen.webkitLockOrientation))
         window.screen.webkitLockOrientation('portrait');
   }
      
   function tmpPopover(el, cont, placement, timeout)
   {
      console.debug(cont);
      //el.popover("destroy");
      el.popover({
         placement: placement,
         content: cont,
         delay: {show: 100, hide: timeout},
         container: el,
         trigger: "manual"});
      console.debug(el.popover);
      el.addClass('text-on-white-theme-<?=$_DOMOTIKA["gui_theme"]?>');
      el.popover("show");
      el.find(".popover-content").html(cont);
      setTimeout(function(){el.popover("destroy")}, timeout);
   }

   function playTTS(text, lang, force)
   {
      if(typeof(force)==='undefined') force=false;
      if(typeof(lang)==='undefined') lang = "it";
      if (!audioTagSupport) return false;
      if (text=='') return false;
      if (ttsEnabled!=1 && force===false) return false;
      if($("playTTS_audio").length)
      {
         var audio = $("playTTS_audio");
      }
      else
      {
         var audio = document.createElement('audio');
         audio.setAttribute('id' , 'playTTS_audio');
      }
      // XXX BUG: webkit based browsers seems to not work with https:// in <audio>, so, we fix this to http
      audio.setAttribute('src', 'http://translate.google.com/translate_tts?tl='+lang+'&q=' + encodeURIComponent(text));
      audio.load();
      audio.play();
      return audio;
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
      console.debug(spobj.serialize());
      $.post("/rest/v1.2/actions/speech_text/json", spobj.serialize(), speechResult );
   }

   // Test SpeechAPI
   var speechStartWord='*terms';
   if((speechEnabled=='touch' && document.createElement('input').webkitSpeech==undefined) || speechEnabled=='continuous')
   {
      if(speechEnabled!='continuous')
      {
         if(window.annyang)
         {
            $("#speechbutton").show(); // it isn't chrome with webkit-speech attribute, but it support WEB Speech API
         }
         else
         {
            $("#speechbutton").hide();
            speechEnabled=='no';
         }
      } else {
         $("#speechbutton").hide();
         speechStartWord='ok domotica *terms';
      }
   } else {
      speechEnabled='touch-chrome';
   }

   function setSpeechText(terms)
   {
      // XXX Sistema sta cosa!
      $("#speech [name=text]").val(terms);
      $("#speechsm [name=text]").val(terms);
      console.debug("SpeechRecognized: "+terms)
      sendSpeech($("#speech"));
   }

   var commands = {
      speechStartWord: setSpeechText 
   };

   if(speechEnabled=='touch' || speechEnabled=='continuous') 
   {
      try {
         annyang.init(commands);
      } catch(err) {
         annyang=null;
      }
      if(annyang) {
         annyang.setLanguage('<?=$_DOMOTIKA['speechlang']?>');
         if(speechEnabled=='continuous')
            annyang.start();
         else if(speechEnabled=='touch')
            annyang.setContinuous(false);
      } else {
         $("#speechbutton").hide();
         speechEnabled='no';
      } 
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

   function calcSnapSize()
   {
      if($(window).width()>768)
         var mval=Math.min(Math.ceil((75/100)*$(window).width()), 800);
      else
         var mval=Math.max(Math.ceil((75/100)*$(window).width()), 266);
      return mval
   }

   $(document).ready(function() {
      mval = calcSnapSize();
      $(".left-drawer").each(function(){ $(this).css("width", mval)});
      $(".right-drawer").each(function(){ $(this).css("width", mval)});
      $(".right-drawer a").each(function(){ 
         if($(this).attr('data-guisection')==GUISECTION){
            //$(this).css('border', '2px solid azure'); 
            $(this).addClass('shadow-<?=$_DOMOTIKA["gui_theme"]?>');
         }
      });
      $(".left-drawer a").each(function(){ 
         if($(this).attr('data-guisubsection')==GUISUBSECTION){
            //$(this).css('border', '2px solid azure'); 
            $(this).addClass('shadow-<?=$_DOMOTIKA["gui_theme"]?>');
         }
      });

   });

   var snapper = new Snap({
      resistance: 0,
      easing: 'linear',
      transitionSpeed: 0.1,
      tapToClose: false,
      element: $('#content')[0],
      dragger: $('#content')[0],
      //dragger: $('[data-domotika-dragger="true"]')[0],
      minDragDistance: 20,
      slideIntent: 30,
      touchToDrag: slideEnabled,
      maxPosition: calcSnapSize(),
      minPosition: -calcSnapSize()
   });

   snapper.on('animating',
      function(e) {
         var mval = calcSnapSize();
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
      var nli='<?=notifyListItem("notify-item-theme-".$_DOMOTIKA["gui_theme"]);?>';
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
      sendSpeech($("#speechsm"));
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
                                          shadowSize: 10,
                                          showinnerShadow: true, 
                                          shadowOpacity: 1
                                      });
         gaugeArray[$(this).attr('id')].refresh($(this).attr('data-dmval')/$(this).attr('data-dmval-divider'));
         $(this).data('gauge', gaugeArray[$(this).attr('id')]);
      }
   );

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
                     if(val[1]<=$(this).attr('data-dmval-min')) {
                        $(this).alterClass('btn-*', $(this).attr('data-dmcolor-min'));
                     } else if(val[1]<=$(this).attr('data-dmval-low')) {
                        $(this).alterClass('btn-*', $(this).attr('data-dmcolor-low'));
                     } else if(val[1]<$(this).attr('data-dmval-high')) {
                        $(this).alterClass('btn-*', $(this).attr('data-dmcolor-med'));
                     } else if(val[1]>=$(this).attr('data-dmval-high')) {
                        $(this).alterClass('btn-*', $(this).attr('data-dmcolor-high'));
                     }

                  }
               );

               $("[data-domotika-anaprog="+val[0]+"]").each(
                  function() {
                     if(val[1]<=$(this).attr('data-dmval-min')) {
                        $(this).alterClass('progress-bar-*', $(this).attr('data-dmcolor-min'));
                     } else if(val[1]<=$(this).attr('data-dmval-low')) {
                        $(this).alterClass('progress-bar-*', $(this).attr('data-dmcolor-low'));
                     } else if(val[1]<$(this).attr('data-dmval-high')) {
                        $(this).alterClass('progress-bar-*', $(this).attr('data-dmcolor-med'));
                     } else if(val[1]>=$(this).attr('data-dmval-high')) {
                        $(this).alterClass('progress-bar-*', $(this).attr('data-dmcolor-high'));
                     }
                  }
               );
               $("[data-domotika-anat="+val[0]+"]").each(
                  function() {
                     v=val[1]/$(this).attr('data-dmval-divider');
                     $(this).text(v);
                  }
               );
               $("[data-domotika-anab="+val[0]+"]").each(
                  function() {
                     v=val[1]/$(this).attr('data-dmval-divider');
                     $(this).text(v);
                  }
               );
               $("[data-domotika-gaugeid="+val[0]+"]").each(
                  function() {
                     $(this).data('gauge').refresh(val[1]/$(this).attr('data-dmval-divider'));
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
                        console.debug($(this));
                        console.debug($(this).attr('data-dmcolor-off'));
                         console.debug($(this).attr('data-dmcolor-on'));
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
         $("#notifyid-"+nt.nid).animate({backgroundColor: notifyColor},3500);
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
      //console.debug("setinterval");
      $.get("/rest/v1.2/keepalive/json", 
         function(r){
            //console.debug(r);
            //console.debug("getok");
            //if('vibrate' in navigator) {
            //   // ... vibrate for a second
            //   navigator.vibrate(1000);
            //}
            if(r.data=='SLOGGEDOUT')
            {
               location.reload();
            }
            if($("#modal_offline").attr('aria-hidden')=='false')
               $("#modal_offline").modal('hide');

         }).fail(function(r){
            console.debug("getfail");
            console.debug(r);
            $("#modal_offline").modal('show');
         }
      );
    },5000);

   $.get("/rest/v1.2/notifications/count/json", function(r){ $("#notifybadge").text(r.data);});

