<? include("common_includes.php"); ?>
<!DOCTYPE html>
<html>
  <head>
    <title>Domotika Admin Dashboard</title>
    <? include("parts/head.php");?>
  </head>
  <body>
<?
   include("parts/alerts.php");
   include("parts/navbar.php");
?>

   <div class="container">

    <h1>Dashboard</h1>

   <div class="row">

    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Q System</h3>
      </div>
      <div class="home-panel">
         <h4>Q Daemon version: <span class="label pull-right">1.0</span></h4>
         <h4>VPN Status: <button type="button" class="btn btn-success btn-small pull-right" style="padding:3px;">ACTIVE</button></h4>
         <h4>IP Address: <span class="label pull-right">192.168.4.11</span></h4>
      </div>
    </div>

    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Boards  
            <a data-toggle="modal" data-dmboard="lock" href="#AutoDetect" class="btn btn-danger btn-small pull-right" style="padding:3px;margin-left:5px;">Autodetect</a>
            <a data-toggle="modal" data-dmboard="lock" href="#Sync" class="btn btn-danger btn-small pull-right" style="padding:3px;">Sync I/O Config</a>
            </h3>
      </div>
         <div class="home-panel">
         <table class="table table-condensed">
            <thead>
               <tr>
                  <th>Board Name</th>
                  <th>Type</th>
                  <th>Level</th>
                  <th>Firmware</th>
               </tr>
            </thead>
            <tbody>
      
<?
      foreach(DB::query("SELECT * FROM dmboards WHERE detected>0") as $board)
      {
         if($board['online']>0) $ttype="success";
         else $ttype="danger";
         ?>
            <tr class="<?=$ttype?>">
               <td><?=$board['name']?></td>
               <td><?=$board['type']?></td>
               <td><?=$board['fwversion']?></td>
               <td><?=$board['fwtype']?></td>
               <td>
                  <!--
                  <button style="margin-left:5px;" type="button" class="btn btn-success btn-small pull-right">Edit</button>
                  -->
                  <button style="margin-left:5px;" type="button" data-dmact="sync" data-boardid="<?=$board['id']?>" class="btn btn-danger btn-small pull-right">Sync</button>
                  <button style="margin-left:5px;" type="button" data-dmact="push" data-boardid="<?=$board['id']?>" class="btn btn-info btn-small pull-right">Push</button>
                  <img src="/resources/preloader/images/animated.gif" data-dmboardload="<?=$board['id']?>" style="height:30px;width:30px;display:none" class="pull-right"></img>
               </td>
            </tr>
         <?
      }
?>
         </tbody>
      </table>
      </div>
    </div>
    <div class="modal fade" id="AutoDetect" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
            <h4 class="modal-title">Board Autodetection</h4>
          </div>
          <div class="modal-body">
            <b>WARNING: </b>you are starting Domotika Boards autodetection procedure. This will
                            delete any dynamic board in the Domotika database and then
                            they will be re-detected. Any change you have made on inputs
                            or outputs, any reference to ID of inputs and outputs will be 
                            deleted or invalidated.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default pull-left" data-dismiss="modal" >Discard</button>
            <input type="checkbox" id="forcedetect">Force detection </input>
            <button type="button" class="btn btn-danger" data-dismiss="modal" id="startdetection">Start Autodetection</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

    <div class="modal fade" id="Sync" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
            <h4 class="modal-title">Board IOConf Sync</h4>
          </div>
          <div class="modal-body">
            <b>WARNING: </b>you are starting Domotika Boards I/O Sync procedure. This will
                            delete any saved board I/O Config in the Domotika database and then
                            they will be re-loaded from the Domotika boards.
                            Any change will be losed.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default pull-left" data-dismiss="modal" >Discard</button>
            <button type="button" class="btn btn-danger" data-dismiss="modal" id="startsync">Start Syncing</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->


    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Timers</h3>
      </div>
      <div class="home-panel">
         <table class="table table-condensed">
            <thead>
               <tr>
                  <th>timer name</th>
                  <th>status</th>
               </tr>
            </thead>
            <tbody>

<?
   foreach(DB::query("SELECT * FROM timers") as $timer)
   {
      ?>
      <tr>
         <td><?=$timer['description']?></td>
         <? if($timer['active']>0) { ?>
         <td><button class="btn btn-success btn-small pull-right">Active</button></td>
         <? } else { ?>
         <td><button class="btn btn-small pull-right">Disabled</button></td>
         <? } ?>
      </tr>
      <?
   }
?>
         </tbody>
      </table>
      </div>
    </div>

    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Users</h3>
      </div>
      <div class="home-panel">
        <table class="table table-condensed">
            <thead>
               <tr>
                  <th>user name</th>
               </tr>
            </thead>
            <tbody>
<?
   foreach(DB::query("SELECT * FROM users") as $user)
   {
      ?>
         <tr>
            <td><?=$user['username']?></td>
         </tr>
      <?
   }
?>
            </tbody>
         </table>

      </div>
    </div>

    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Last news</h3>
      </div>
      <div class="home-panel">
         <h3>Benvenuti in Domotika!</h3>
         <p>Grazie per aver scelto il piu' avanzato sistema domotico esistente!
         </p>
      </div>
    </div>

    <div class="panel col-lg-4">
      <div class="panel-heading">
         <h3 class="panel-title">Media/Video</h3>
      </div>
      <div class="home-panel">
         <table class="table table-condensed">
            <thead>
               <tr>
                  <th>name</th>
                  <th>websection</th>
                  <th>dynamic</th>
                  <th>channels</th>
               </tr>
            </thead>
            <tbody>
<?
   foreach(DB::query("SELECT * FROM mediasources") as $video)
   {
      ?>
         <tr>
            <td><?=$video['button_name']?></td>
            <td><?=$video['websection']?></td>
            <td><?if($video['dynamic']==1){echo 'yes';}else{echo 'no';}?></td>
            <td>
<?
   if($video['has_channels']=='yes')
   {
      ?>
               <a data-toggle="modal" href="#" class="btn btn-danger btn-small" style="padding:3px;">Scan</a>
      <?
   } else {
      echo "-";
   }
?>
            </td>
         </tr>
      <?
   }
?>

            </tbody>
         </table>

         </p>
      </div>
    </div>


   </div>

   </div> <!-- container -->
   <?include("parts/foot.php");?>
   <script type="text/javascript">

      function lockGlobalBoards()
      {
         $("[data-dmboard=lock]").each(
            function(){
               $(this).attr("disabled","true");
            }
         );
      }


      function lockAllBoards()
      {
         $("[data-dmact=sync]").each(
            function(){
               $(this).attr("disabled","true");
            }
         );
         $("[data-dmact=push]").each(
            function(){
               $(this).attr("disabled","true");
            }
         );
         $("[data-dmboardload]").each(
           function(){
               $(this).css("display","block");
            }
         );
         lockGlobalBoards();
      }



      $("#startdetection").click(
         function() {
            if($('#forcedetect').is(":checked"))
               $.get("/rest/v1.2/boards/forceautodetect/json");
            else
               $.get("/rest/v1.2/boards/autodetect/json");
         }
      );
      $("#startsync").click(
         function() {
            lockAllBoards();
            $.get("/rest/v1.2/boards/syncall/json");
         }
      );

      $("[data-dmact=push]").click(
         function() {
            $("[data-dmboardload="+$(this).attr('data-boardid')+"]").each(
               function(){
                  $(this).css("display","block");
               }
            );
            $(this).attr('disabled', true);
            $("[data-dmact=sync][data-boardid="+$(this).attr('data-boardid')+"]").each(
               function() {
                  $(this).attr('disabled', true);
               }
            );
            lockGlobalBoards();
            $.get("/rest/v1.2/boards/pushboardbyid/"+$(this).attr('data-boardid')+"/json");
         }
      )
      $("[data-dmact=sync]").click(
         function() {
            $("[data-dmboardload="+$(this).attr('data-boardid')+"]").each(
               function(){
                  $(this).css("display","block");
               }
            );
            $(this).attr('disabled', true);
            $("[data-dmact=push][data-boardid="+$(this).attr('data-boardid')+"]").each(
               function() {
                  $(this).attr('disabled', true);
               }
            );
            lockGlobalBoards();
            $.get("/rest/v1.2/boards/syncboardbyid/"+$(this).attr('data-boardid')+"/json");
         }
      )


   </script>
  </body>
</html>
