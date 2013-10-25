<? 
@include_once("../includes/common.php"); 
?>
    <h1>Settings</h1>
<ul class="nav nav-tabs">
  <li <? if($GUISUBSECTION=="") {?>class="active"<?}?>><a href="<?=$BASEGUIPATH.'/'.$GUISECTION?>">User options</a></li>
  <li <? if($GUISUBSECTION=="gui") {?>class="active"<?}?>><a href="<?=$BASEGUIPATH.'/'.$GUISECTION?>/gui">GUI options</a></li>
</ul>
<? if($GUISUBSECTION=="") {?>
<div class="formcontainer">
<form id="userform" name="userform" class="form-horizontal" style="display:none">
   <div class="form-group">
      <label for="username" class="col-lg-2 control-label">Username:</label>
      <div class="col-lg-3">
         <h4 id="username">username</h4>
      </div>
   </div>
   <div class="form-group">
      <label for="email" class="col-lg-2 control-label">Email:</label>
      <div class="col-lg-3">
         <input type="text" class="form-control" id="email" name="email" placeholder="your@email.tld">
      </div>
   </div>
   <div class="form-group">
      <label for="pwd1" class="col-lg-2 control-label">Password:</label>
      <div class="col-lg-3">
         <input type="password" class="form-control" id="pwd1" name="passwd" placeholder="password or blank">
      </div>
   </div>
   <div class="form-group">
      <label for="pwd2" class="col-lg-2 control-label">Repeat password:</label>
      <div class="col-lg-3">
         <input type="password" class="form-control" id="pwd2" name="pwd2" placeholder="password or blank">
      </div>
   </div>
   <div class="form-group">
      <label for="desktophome" class="col-lg-2 control-label">Desktop Homepath:</label>
      <div class="col-lg-3">
         <input type="text" class="form-control" id="desktophome" name="desktop_homepath" placeholder="">
      </div>
   </div>
   <div class="form-group">
      <label for="mobilehome" class="col-lg-2 control-label">Mobile Homepath:</label>
      <div class="col-lg-3">
         <input type="text" class="form-control" id="mobilehome" name="mobile_homepath" placeholder="">
      </div>
   </div>
   <div class="form-group">
      <label for="lang" class="col-lg-2 control-label">Lang:</label>
      <div class="col-lg-3">
         <select name="lang" id="lang" class="form-control">
            <option value="it">italiano</option>
            <option value="en">english</option>
         </select>
      </div>
   </div>
   <div class="form-group">
      <label for="tts" class="col-lg-2 control-label">Enable TTS:</label>
      <div class="col-lg-3">
         <div class="make-switch switch-mini" id="tts-switch" data-on-label="YES" data-off-label="NO">
            <input id="tts" type="radio" name="tts" />
         </div>
      </div>
   </div>
   <div class="form-group">
   <label for="mobilehome" class="col-lg-2 control-label"></label>
      <div class="col-lg-3">
         <input type="submit" value="Save"  class="btn btn-default">
      </div>
   </div>
</form>
<div>
<?} elseif($GUISUBSECTION=="gui") { // $GUISUBSECTIONOPT?>
<ul class="nav nav-pills nav-stacked">
  <li class="active"><a href="#">Home</a></li>
  <li><a href="#">Profile</a></li>
  <li><a href="#">Messages</a></li>
</ul>
<div class="formcontainer">
<form id="userform" name="userform" class="form-horizontal">
   <div class="form-group">
      <label for="username" class="col-lg-2 control-label">Username:</label>
      <div class="col-lg-3">
         <h4 id="username">username</h4>
      </div>
   </div>
   <div class="form-group">
      <label for="email" class="col-lg-2 control-label">Email:</label>
      <div class="col-lg-3">
         <input type="text" class="form-control" id="email" name="email" placeholder="your@email.tld">
      </div>
   </div>

</form>
</div>
<?} else  {
   header("Location: $BASEGUIPATH/settings");
   exit(0); 
}?>
