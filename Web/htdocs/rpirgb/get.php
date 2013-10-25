<?
include("common_includes.php");
   $color=wget("http://localhost:9980/");
   $color="rgb(".str_replace("RGB:", "", $color).")";
   echo $color;
?>
