var conn = null;
var ellog = null;
var wsprot="ws";
var keepAlive=null;
var keepAliveUri = null;
var keepAliveTime = 600000; // time in milliseconds

$.domotikaDebug=false;

function connectSocket(socktype, sockuri, wsprot)
{
   var c=null;
   log("try to connect " + sockuri + " using " + socktype + " protocol " + wsprot );
   if ("WebSocket" in window) {
      c = new WebSocket(wsuri);
   } else if ("MozWebSocket" in window) {
      c = new MozWebSocket(wsuri);
   } else {
      c = new SockJS(sockuri,null,{debug:true,devel:true,protocols_whitelist:[wsprot]});
   }
   return c;
}

function initSockets() {
   ellog = document.getElementById('log');
   if(window.location.port!="") {
      if(window.location.protocol === "https:") {
         wsuri = "wss://" + window.location.hostname + ":"+window.location.port+"/autobahn";
         wsprot = "wss"
      } else {
         wsuri = "ws://" + window.location.hostname + ":"+window.location.port+"/autobahn";
      }
      sockjsuri = window.location.protocol+'//'+window.location.hostname+':'+window.location.port+'/sockjs';
      keepAliveUri = window.location.protocol+'//'+window.location.hostname+':'+window.location.port+'/rest/v1.0/keepAlive';
   } else {
      if(window.location.protocol === "https:") {
         wsuri = "wss://" + window.location.hostname + "/autobahn";
         wsprot = "wss"
      } else {
         wsuri = "ws://" + window.location.hostname +"/autobahn";
      }
      sockjsuri = window.location.protocol+'//'+window.location.hostname+'/sockjs';
      keepAliveUri = window.location.protocol+'//'+window.location.hostname+'/rest/v1.0/keepAlive';
   }
   if("WebSocket" in window || "MozWebSocket" in window) {
      socktype="autobahn";
      conn = connectSocket(socktype, wsuri, wsprot);

   } else {
      sjsprots=new Array('xdr-streaming','xhr-streaming','iframe-eventsource','iframe-htmlfile','xdr-polling','xhr-polling','iframe-xhr-polling','jsonp-polling');
      socktype="sockjs";
      sjidx=0;
      wsprot=sjsprots[sjidx]
      conn = connectSocket(socktype, sockjsuri, wsprot);
   }
   attachSockEvents();
   keepAlive=setInterval(function(){ $.get(keepAliveUri); }, keepAliveTime);
 };
 function attachSockEvents() {
   if (conn) {
      conn.onopen = function(e) {
         if(socktype=="autobahn")
            sockurl = wsuri;
         else
            sockurl = sockjsuri;
         log("Connected to " + sockurl + " using " + socktype + " protocol " + wsprot +", test connection" );
         conn.send("testconn");
         if(typeof $.onDomotikaConnected == "function")
            $.onDomotikaConnected(e);
      };

      conn.onclose = function(e) {
         log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
         if(typeof $.onDomotikaDisconnected == "function")
            $.onDomotikaDisconnected(e);
         conn = null;
         if(e.wasClean===false)
         {
            if(e.code==2000 && socktype=="sockjs")
            {
               if(sjidx<sjsprots.length-1) {
                  sjidx++;
                  var wait=0;
               } else {
                  sjidx=0;
                  var wait=3000;
               }
            }
            if(socktype=="autobahn") {
               conn = connectSocket(socktype, wsuri, wsprot);
               attachSockEvents();
            } else {
               wsprot=sjsprots[sjidx];
               if(wait > 0) {
                  log("<br>DELAY RECONNECTION\r\n");
                  setTimeout(function(){conn = connectSocket(socktype,sockjsuri,wsprot); attachSockEvents();},wait);
               } else {
                  conn = connectSocket(socktype, sockjsuri, wsprot);
                  attachSockEvents();
               }
            }

         }
      };

      conn.onmessage = function(e) {
         log("Received: " + e.data);
         if(typeof $.onDomotikaMessage == "function")
            $.onDomotikaMessage(e);
      };
   } else {
      alert('NoSock');
   }
};

function send() {
   var msg = document.getElementById('message').value;
   if (conn) {
      conn.send(msg);
      log("Sent: " + msg);
   } else {
      log("Not connected.");
   }
};


function domotikaSend(msg) {
   if (conn) {
      try {
         conn.send(msg);
         log("Sent: " + msg);
      } catch(err) {
         log(err);
      }
   } else {
      log("Not connected.");
   }
}

function log(m) {
   if(ellog)
   {
      ellog.innerHTML += m + '\r\n';
      ellog.scrollTop = ellog.scrollHeight;
   } else {
      if($.domotikaDebug)
         console.log(m);
   }
};

if(window.addEventListener){
   window.addEventListener('online', function(){
      if(conn)
         conn.close();
      conn = false;
      initSockets();
   });

   window.addEventListener('offline', function(){
      if(conn)
         conn.close();
      conn = false;
      if(keepAlive)
         clearInterval(keepAlive);
   });
}else{
   window.addEvent('online', function(){
      if(conn)
         conn.close();
      conn = false;
      initSockets();
   });

   window.addEvent('offline', function(){
      if(conn)
         conn.close();
      conn = false;
   });
}



