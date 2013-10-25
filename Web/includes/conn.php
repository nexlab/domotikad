<?php
$conn = mysql_connect(DBHOST,DBUSER,DBPASS, true);
mysql_select_db (DBNAME, $conn);
mysql_query("SET NAMES utf8");
mysql_query("SET CHARACTER SET utf8");

DB::$user = DBUSER;
DB::$password = DBPASS;
DB::$dbName = DBNAME;
DB::$host = DBHOST;
DB::$encoding = 'utf8';

?>

