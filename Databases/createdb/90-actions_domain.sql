ALTER TABLE  `actions` ADD  `select_domain` VARCHAR( 32 ) NOT NULL AFTER  `launch_sequence_name` , ADD INDEX (  `select_domain` ) ;
