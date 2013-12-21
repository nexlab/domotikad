ALTER TABLE  `voip_users` ADD  `callbackextension` VARCHAR( 255 ) NULL DEFAULT NULL AFTER  `secret`;
ALTER TABLE  `voip_users` ADD INDEX (  `callbackextension` );
ALTER TABLE  `voip_users` ADD  `regserver` VARCHAR( 100 ) NULL DEFAULT NULL AFTER  `insecure` , ADD INDEX (  `regserver` );
UPDATE voip_users SET nat='force_rport,comedia instead' WHERE nat='yes';
ALTER TABLE  `voip_users` ADD  `avpf` ENUM(  'no',  'yes' ) NOT NULL DEFAULT  'no' AFTER  `transport`;
ALTER TABLE  `voip_users` ADD  `encryption` ENUM(  'no',  'yes' ) NOT NULL DEFAULT  'no' AFTER  `avpf`;
ALTER TABLE  `voip_users` CHANGE  `nat`  `nat` ENUM(  'force_rport,comedia',  'no',  'force_rport',  'comedia' ) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT  'force_rport,comedia';
