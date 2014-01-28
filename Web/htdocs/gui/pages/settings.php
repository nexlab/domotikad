<? 
@include_once("../includes/common.php"); 
?>
    <h1>Settings</h1>
<ul class="nav nav-tabs">
  <li <? if($GUISUBSECTION=="") {?>class="active"<?}?>><a href="<?=$BASEGUIPATH.'/'.$GUISECTION?>">User options</a></li>
 <!-- <li <? if($GUISUBSECTION=="gui") {?>class="active"<?}?>><a href="<?=$BASEGUIPATH.'/'.$GUISECTION?>/gui">GUI options</a></li> -->
</ul>
<? if($GUISUBSECTION=="") {?>
<div class="formcontainer" >
<form id="userform" name="userform" class="form-horizontal" style="display:none;margin-bottom:60px;">
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
      <label for="slide" class="col-lg-2 control-label">Sliding GUI:</label>
      <div class="col-lg-3">
         <div class="make-switch switch-mini" id="slide-switch" data-on-label="YES" data-off-label="NO">
            <input id="slide" type="radio" name="slide" />
         </div>
      </div>
   </div>
   <div class="form-group">
      <label for="webspeech" class="col-lg-2 control-label">Web Speech rec.:</label>
      <div class="col-lg-3">
         <select name="webspeech" id="webspeech" class="form-control">
            <option value="no">no</option>
            <option value="touch">touch</option>
            <option value="continuous">continuous</option>
         </select>
      </div>
   </div>
   <div class="form-group">
      <label for="speechlang" class="col-lg-2 control-label">Speech lang:</label>
      <div class="col-lg-3">
         <select name="speechlang" id="speechlang" class="form-control">
            <option value="en-US">US English</option>
            <option value="en-GB">UK English</option>
            <option value="it-IT">IT Italiano</option>
            <option value="it-CH">CH Italiano</option>
         </select>
      </div>
   </div>
   <div class="form-group">
      <label for="gui_theme" class="col-lg-2 control-label">GUI Theme:</label>
      <div class="col-lg-3">
         <select name="gui_theme" id="gui_theme" class="form-control">
            <option value="dmblack">DM Black</option>
            <option value="dmwhite">DM White</option>
         </select>
      </div>
   </div>
   <div class="form-group">
      <label for="leftb" class="col-lg-2 control-label">Left bar visibility:</label>
      <div class="col-lg-3">
         <select name="leftb" id="leftb" class="form-control">
            <option value="all">All sizes</option>
            <option value="none">No</option>
            <option value="visible-sm">Small only</option>
            <option value="visible-md">Medium only</option>
            <option value="visible-lg">Big only</option>
            <option value="hidden-sm">All but small</option>
            <option value="hidden-md">All but medium</option>
            <option value="hidden-lg">All but big</option>
         </select>
      </div>
   </div>
   <div class="form-group">
      <label for="rightb" class="col-lg-2 control-label">Left bar visibility:</label>
      <div class="col-lg-3">
         <select name="rightb" id="rightb" class="form-control">
            <option value="all">All sizes</option>
            <option value="none">No</option>
            <option value="visible-sm">Small only</option>
            <option value="visible-md">Medium only</option>
            <option value="visible-lg">Big only</option>
            <option value="hidden-sm">All but small</option>
            <option value="hidden-md">All but medium</option>
            <option value="hidden-lg">All but big</option>
         </select>
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
<?}/* elseif($GUISUBSECTION=="gui") { // $GUISUBSECTIONOPT?>
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
<?} */ else  {
   header("Location: $BASEGUIPATH/settings");
   exit(0); 
}?>
