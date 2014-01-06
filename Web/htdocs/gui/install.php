<? include("includes/common.php");
?><html>
<head>
</head>
<body>
<button id="install">
  Install Domotika GUI on homescreen
</button>
 
<script>
(function(){
  function install(ev) {
    ev.preventDefault();
    // define the manifest URL
    var port="";
    if(document.location.port)
      var port=":"+document.location.port;
    var manifest_url = document.location.protocol+"//"+document.location.host+port+"<?=str_replace("/install.php","",$BASEGUIPATH)?>/manifest.webapp";
    // install the app
    var myapp = navigator.mozApps.install(manifest_url);
    myapp.onsuccess = function(data) {
      // App is installed, remove button
      //this.parentNode.removeChild(this);
      console.log(this);
    };
    myapp.onerror = function() {
      // App wasn't installed, info is in this.error.name
      console.log('Install failed, error: ' + this.error.name);
     };
  };
  // get a reference to the button and call install() on click
  var button = document.getElementById('install');
  button.addEventListener('click', install, false);
})();
</script>
</body>
</html>
