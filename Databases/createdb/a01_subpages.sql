ALTER TABLE  `user_gui_panels` ADD  `subpage` VARCHAR( 1024 ) NOT NULL AFTER  `page` ,
ADD INDEX (  `subpage` ) ;
ALTER TABLE  `users` ADD  `configlock` ENUM(  'yes',  'no' ) NOT NULL DEFAULT  'no',
ADD INDEX (  `configlock` ) ;
