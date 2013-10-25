<? include("includes/common.php"); 
ob_start(); 
include("parts/head.php");
$PAGE_BUFFER['head'] = ob_get_clean(); 

ob_start();
include("parts/alerts.php");
$PAGE_BUFFER['alerts'] = ob_get_clean();


ob_start(); 
include("parts/navbar.php");
$PAGE_BUFFER['navbar'] = ob_get_clean();

ob_start();
if($left)
  include("left/$GUISECTION.php");
$PAGE_BUFFER['left_drawer'] = ob_get_clean();

ob_start();
if($right)
  include("right/$GUISECTION.php");
$PAGE_BUFFER['right_drawer'] = ob_get_clean();

ob_start();
if($GUIPATH=='/')
  include("pages/index.php");
else
{
  if(file_exists("pages/$GUISECTION.php"))
    include("pages/$GUISECTION.php");
  else
    include("pages/404.php");
}
$PAGE_BUFFER['content'] = ob_get_clean();

ob_start();
include("parts/footbar.php");
$PAGE_BUFFER['footbar'] = ob_get_clean();

ob_start();
include("parts/foot.php");
$PAGE_BUFFER['foot'] = ob_get_clean();

ob_start();
if(file_exists("footjs/$GUISECTION.php"))
  include("footjs/$GUISECTION.php");
$PAGE_BUFFER['footjs'] = ob_get_clean();
if(file_exists("heads/$GUISECTION.php"))
   addHead("heads/$GUISECTION.php");
include_once("includes/page.php");?>
