ALTER TABLE  `actions` ADD  `select_domain` VARCHAR( 32 ) NOT NULL AFTER  `launch_sequence_name` , ADD INDEX (  `select_domain` ) ;
ALTER TABLE  `user_gui_panels` CHANGE  `panel_selector`  `panel_selector` ENUM(  'any',  'dmdomain') CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT  'any';
