ALTER TABLE  `actions` ADD  `rcv_src` VARCHAR( 32 ) NOT NULL DEFAULT  '*' AFTER  `rcv_dst` ,
ADD INDEX (  `rcv_src` ) ;
ALTER TABLE  `stats_charts_series` CHANGE  `selector_type`  `selector_type` ENUM(  'SQL',  'daily_sum',  'hourly_sum' ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT  'SQL';
