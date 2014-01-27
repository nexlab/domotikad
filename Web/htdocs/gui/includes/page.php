<!DOCTYPE html>
<?
/*
<html manifest="<?=$BASEGUIPATH?>/offline.appcache">
*/
?><html>
  <head>
<?=$PAGE_BUFFER['head']?>
<?=$PAGE_ADDHEAD?>
  </head>
  <body class="scrollable-vertical theme-<?=$_DOMOTIKA['gui_theme']?>">
<?=$PAGE_BUFFER['alerts']?>
<?=$PAGE_BUFFER['navbar']?>
   <div class="drawers">
<?=$PAGE_BUFFER['left_drawer']?>
<?=$PAGE_ADDLEFT?>
<?=$PAGE_BUFFER['right_drawer']?>
<?=$PAGE_ADDRIGHT?>
   </div> <!-- drawers -->
   <div id="content" class="primarycontainer scrollable-vertical theme-<?=$_DOMOTIKA['gui_theme']?>">
   <div class="container theme-<?=$_DOMOTIKA['gui_theme']?>">
<?=$PAGE_BUFFER['content']?>
   </div> <!-- container -->
   </div> <!-- primarycontainer -->
<?=$PAGE_BUFFER['footbar']?>
<?=$PAGE_BUFFER['foot']?>
<?=$PAGE_BUFFER['footjs']?>
<?=$PAGE_ADDFOOTJS?>
  </body>
</html>

