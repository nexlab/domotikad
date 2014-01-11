<? @include_once("../includes/common.php"); ?>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <title>Domotika GUI - <?=$tr->Get($GUISECTION)?></title>


    <!-- Allow fullscreen mode on iOS devices. (These are Apple specific meta tags.) -->
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black" />
    <link rel="apple-touch-icon" sizes="256x256" href="/resources/img/logo_icon.png" />
    <meta name="HandheldFriendly" content="true" />

    <!-- Chrome for Android web app tags -->
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="shortcut icon" sizes="256x256" href="/resources/img/logo_icon.png" />
    <? if($GUIDEBUG) { ?>
    <!-- Bootstrap -->
    <link href="/resources/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="/resources/glyphicons/css/bootstrap-glyphicons.css" rel="stylesheet" media="screen">
    <link href="/resources/full-glyphicons/css/glyphicons.css" rel="stylesheet" media="screen">
    <link href="/resources/bootstrap-switch/static/stylesheets/bootstrap-switch.css" rel="stylesheet" media="screen">
    <link href="<?=$BASEGUIPATH;?>/css/style.css" rel="stylesheet" media="screen" />
    <? } else { ?>
    <link href="<?=$BASEGUIPATH;?>/css/combined.min.css" rel="stylesheet" media="screen" />
    <link href="<?=$BASEGUIPATH;?>/css/style.css" rel="stylesheet" media="screen" />
    <? } ?>
