<? @include_once("../includes/common.php");?>
    <? if($GUIDEBUG) { ?>
    <!-- JavaScript plugins (requires jQuery) -->
    <script src="/resources/js/jquery-1.10.2.min.js"></script>
    <script src="/resources/jquery-color/jquery.color.js"></script>
    <script src="/resources/hammer.js/hammer.min.js"></script> 
    <script src="/resources/hammer.js/plugins/hammer.fakemultitouch.js"></script>
    <!--[if !IE]> -->
    <script src="<?=$BASEGUIPATH;?>/js/starthammer.js"></script>
    <!-- <![endif]-->
    <script src="/resources/hammer.js/plugins/jquery.hammer.js/jquery.hammer.min.js"></script>
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
    <!-- jquery easing plugin -->
    <script src="/resources/js/jquery.easing.1.3.min.js"></script>
    <script src="/resources/js/jquery.alterclass.js"></script>
    <script src="<?=$BASEGUIPATH;?>/js/fastclick.js"></script>
    <script src="<?=$BASEGUIPATH;?>/js/speech.js"></script>
    <script src="<?=$BASEGUIPATH;?>/js/domotika.js"></script>
   <? } else { ?>
   <script src="<?=$BASEGUIPATH;?>/js/combined.min.js"></script>
    <script src="<?=$BASEGUIPATH;?>/js/domotika.js"></script>
   <? } ?>
