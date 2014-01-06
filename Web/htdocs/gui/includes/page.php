<!DOCTYPE html>
<html manifest="<?=$BASEGUIPATH?>/offline.appcache">
  <head>
<?=$PAGE_BUFFER['head']?>
<?=$PAGE_ADDHEAD?>
  </head>
  <body>
<?=$PAGE_BUFFER['alerts']?>
<?=$PAGE_BUFFER['navbar']?>
   <div class="drawers">
<?=$PAGE_BUFFER['left_drawer']?>
<?=$PAGE_ADDLEFT?>
<?=$PAGE_BUFFER['right_drawer']?>
<?=$PAGE_ADDRIGHT?>
   </div> <!-- drawers -->
   <div id="content" class="primarycontainer scrollable">
   <div class="container">
<?=$PAGE_BUFFER['content']?>
   </div> <!-- container -->
   </div> <!-- primarycontainer -->
<?=$PAGE_BUFFER['footbar']?>
<?=$PAGE_BUFFER['foot']?>
<?=$PAGE_BUFFER['footjs']?>
<?=$PAGE_ADDFOOTJS?>
  </body>
</html>

