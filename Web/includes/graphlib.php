<?
include_once("common_includes.php");

function formatPoints($x, $y)
{
   $line="[";
   if( is_numeric($x))
      $line.=$x.",";
   else
      $line.="'".$x."',";
   if( is_numeric($y))
      $line.=$y;
   else
      $line.="'".$y."'";
   $line.="]";
   return $line;
}

function getSelectorSubtype($serie)
{
   $query="";
   if($serie["selector_subtype"]=="back_in_time")
   {
      //$daysql = getLastNDays(intval($serie["selector_numopt"]), 'Y-m-d');
      //$query.=" AND date <= '".$daysql[count($daysql)-1]."'";
      //$query.=" AND date <= DATE_FORMAT(NOW(), '%Y-%d-%m %H:%i:%S')";
      //$query.=" AND date >= '".$daysql[0]."'";
      $query.=" AND date >= DATE_ADD(NOW(),";
      $query.=" INTERVAL -".strval($serie["selector_numopt"])." DAY)";
   } elseif($serie["selector_subtype"]=="limits")
   {
      if($serie["selector_start"])
        $query.=" AND date >= '".$serie["selector_start"]."'";
      if($serie["selector_stop"])
        $query.=" AND date <= '".$serie["selector_stop"]."'";
   }
   return $query;
}

function applyCoefficients($x, $y, $serie)
{
   if(is_numeric($x)) {
      if($serie['x_coefficient'] != 'equal' && (float)$serie['x_coefficient_val'] != (float)0)
      {
         if($serie['x_coefficient']=='divider')
            $x=(float)$x/(float)($serie['x_coefficient_val']);
         elseif($serie['x_coefficient']=='moltiplier')
            $x=(float)$x*(float)($serie['x_coefficient_val']);
      }
   }
   if(is_numeric($y)) {
      if($serie['y_coefficient'] != 'equal' && (float)$serie['y_coefficient_val'] != (float)0)
      {
         if($serie['y_coefficient']=='divider')
            $y=(float)$y/(float)($serie['y_coefficient_val']);
         elseif($serie['y_coefficient']=='moltiplier')
            $y=(float)$y*(float)($serie['y_coefficient_val']);
      }
   }
   return array('x'=>$x,'y'=> $y);
}

function parseSelectorName($cmd, $serie)
{
   $cmd = str_replace("#OPTNUM#", $serie["selector_numopt"], $cmd);
   $cmd = str_replace("#NAME#", $serie["name"], $cmd);
   $cmd = str_replace("#START#", $serie["selector_start"], $cmd);
   $cmd = str_replace("#STOP#", $serie["selector_stop"], $cmd);
   $cmd = str_replace("#SUBTYPE#", $serie["selector_subtype"], $cmd);
   $cmd = str_replace("#ID#", $serie["id"], $cmd);
   return $cmd;

}

function getChartData($chartname)
{
   /*
    * take the name of the chart in input,
    * give a pre-formatted nested list for chart data
    * as a php array with int index in the form of:
    *
    * array(
    *    idx => array(
    *       data => "[[x1,y1],[x2,y2]...]",
    *       serie => array("option1" => "value1", "option2 => ...)
    *    )
    * )
    *       
    *
    *         
    */
   $ret=array();
   $idx=0;
   $series=DB::query("SELECT * FROM stats_charts_series WHERE active=1 AND name='".$chartname."'");
   foreach($series as $serie)
   {
      switch($serie['selector_type'])
      {
         case "SQL":
               $seriesret=DB::query($serie['selector_name']);
            break;
         case "script":
            $seriesret=array();
            $cmd = parseSelectorName($serie['selector_name'], $serie);
            $script = explode("\n", str_replace("\r", "", shell_exec($cmd)));
            foreach($script as $currentLine)
            {
               $currentLine = explode(":", $currentLine);
               if(count($currentLine)>=2)
                  $seriesret[]=array('x' => $currentLine[0], 'y' => $currentLine[1]);
            }
            
            break;
         case "file":
            $seriesret=array();
            $file = @fopen(parseSelectorName($serie['selector_name'], $serie), "r"); 
            while (!feof($file))
            {
               $currentLine = explode(":", fgets($file));
               if(count($currentLine)>=2)
                  $seriesret[]=array('x' => $currentLine[0], 'y' => $currentLine[1]);
            }
            break;
         case "daily_sum":
            $query="SELECT date as 'x',SUM(";
            for($h=0;$h<24;$h++)
            {
               $query.="h".zfill($h,2);
               if($h<23)
                  $query.="+";
            }
            $query.=") as 'y' FROM stats_history WHERE";
            if(startsWith($serie['selector_name'], "like:"))
            {
               $selectorname=parseSelectorName(str_replace("like:","",$serie['selector_name']),$serie);
               $query.=" name LIKE '".$selectorname."'";
            }
            elseif(startsWith($serie['selector_name'], "dmdomain:"))
            {
               $selectorname=parseSelectorName(str_replace("dmdomain:","",$serie['selector_name']),$serie);
               $query.=" DMDOMAIN(name, '".$selectorname."')=1";
            }
            else
            {
               $query.=" name='".parseSelectorName($serie['selector_name'], $serie)."'";
            }
            $query.=getSelectorSubtype($serie);
            $query.=" group by date";
            $seriesret=DB::query($query);
            break;
         case "hourly_sum":
            $seriesret=array();
            $query="SELECT date";
            for($h=0;$h<24;$h++)
            {
               $query.=",SUM(h".zfill($h,2).") as h".zfill($h,2);
            }

            $query.=" FROM stats_history WHERE";
            if(startsWith($serie['selector_name'], "like:"))
            {
               $selectorname=parseSelectorName(str_replace("like:","",$serie['selector_name']),$serie);
               $query.=" name LIKE '".$selectorname."'";
            }
            elseif(startsWith($serie['selector_name'], "dmdomain:"))
            {
               $selectorname=parseSelectorName(str_replace("dmdomain:","",$serie['selector_name']),$serie);
               $query.=" DMDOMAIN(name, '".$selectorname."')=1";
            }
            else
            {
               $query.=" name='".parseSelectorName($serie['selector_name'], $serie)."'";
            }  
            $query.=getSelectorSubtype($serie);
            $query.=" group by date";
            $tmpret=DB::query($query);
            foreach($tmpret as $entry)
            {
               if($serie['selector_subtype']=='back_in_time' && date('Y-m-d')==$entry["date"])
                  $maxh=date('H');
               else
                  $maxh=23;
               for($h=0;$h<=$maxh;$h++)
               {
                  $x=$entry["date"];
                  $x.=" ".zfill($h,2).":00AM";
                  $y=$entry["h".zfill($h,2)];
                  $seriesret[] = array('x' => $x, 'y' => $y);
               } 
            }
            break;
      }
      $line="[";
      $i=0;
      foreach($seriesret as $point)
      {
         $xy=applyCoefficients($point['x'], $point['y'], $serie);
         $i++;
         $line.=formatPoints($xy['x'], $xy['y']);
         if(count($seriesret) > $i)
         {
            $line.=',';
         }
      }
      $line.="]";
      $ret[$idx] = array('data' => $line, 'serie' => $serie, 'count' => count($seriesret));
      $idx++;
   }
   return $ret;
}

?>
