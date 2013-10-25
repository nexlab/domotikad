<?
function getLastNDays($days, $format = 'd/m', $forphp=false){
    $m = date("m"); $de= date("d"); $y= date("Y");
    $dateArray = array();
    for($i=0; $i<=$days-1; $i++){
        if($forphp)
            $dateArray[] = date($format, mktime(0,0,0,$m,($de-$i),$y));
        else
            $dateArray[] = date($format, mktime(0,0,0,$m,($de-$i),$y)); 
    }
    return array_reverse($dateArray);
}

function zfill($n,$a) {
  return str_repeat("0",max(0,$a-strlen($n))).$n;
}

function startsWith($haystack, $needle)
{   
    return $needle === "" || strpos($haystack, $needle) === 0;
}
function endsWith($haystack, $needle)
{   
    return $needle === "" || substr($haystack, -strlen($needle)) === $needle;
}

?>
