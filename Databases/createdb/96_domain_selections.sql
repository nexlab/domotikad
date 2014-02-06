ALTER TABLE  `actions` DROP  `select_domain` ;
ALTER TABLE  `actions` ADD  `action_name` VARCHAR( 32 ) NOT NULL AFTER  `id` ,
ADD INDEX (  `action_name` ) ;
ALTER TABLE  `timers` CHANGE  `timer_name`  `description` VARCHAR( 255 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ;
ALTER TABLE  `timers` ADD  `timer_name` VARCHAR( 32 ) NOT NULL AFTER  `id` ,
ADD INDEX (  `timer_name` ) ;
ALTER TABLE  `speech_actions` CHANGE  `speechaction_name`  `speechaction_name` VARCHAR( 32 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ;
ALTER TABLE  `statuses` CHANGE  `status_name`  `status_name` VARCHAR( 32 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ;
ALTER TABLE  `statuses` CHANGE  `trigger`  `status_trigger` VARCHAR( 1024 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ;
ALTER TABLE  `statusrealtime` CHANGE  `status_name`  `status_name` VARCHAR( 32 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL ;
ALTER TABLE  `status_actions` CHANGE  `status_name`  `status_name` VARCHAR( 32 ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL ;
ALTER TABLE  `user_gui_panels` CHANGE  `panel_type`  `panel_type` ENUM(  'standard',  'gauge',  'graph',  'macrobuttons',  'bookmarks',  'cameras',  'video',  'gxv3175_left',  'gxv3175_center',  'gxv3175_right' ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT  'standard';
