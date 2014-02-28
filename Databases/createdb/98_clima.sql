ALTER TABLE  `ioconf_analogs` ADD  `take_in_sync` ENUM(  'yes',  'no' ) NOT NULL DEFAULT  'no' AFTER  `status_name` ,
ADD  `sync_direction` ENUM(  'board2domotika',  'domotika2board' ) NOT NULL DEFAULT  'domotika2board' AFTER  `take_in_sync` ,
ADD  `sync_interval` INT UNSIGNED NOT NULL AFTER  `sync_direction` ,
ADD INDEX (  `take_in_sync` ,  `sync_direction` ) ;
ALTER TABLE  `ioconf_outputs` ADD  `take_in_sync` ENUM(  'yes',  'no' ) NOT NULL DEFAULT  'no' AFTER  `outnum` ,
ADD  `sync_direction` ENUM(  'board2domotika',  'domotika2board' ) NOT NULL DEFAULT  'domotika2board' AFTER  `take_in_sync` ,
ADD  `sync_interval` INT UNSIGNED NOT NULL AFTER  `sync_direction` ,
ADD INDEX (  `take_in_sync` ,  `sync_direction` ) ;
ALTER TABLE  `ioconf_inputs` ADD  `take_in_sync` ENUM(  'yes',  'no' ) NOT NULL DEFAULT  'no' AFTER  `status_name` ,
ADD  `sync_direction` ENUM(  'board2domotika',  'domotika2board' ) NOT NULL DEFAULT  'domotika2board' AFTER  `take_in_sync` ,
ADD  `sync_interval` INT UNSIGNED NOT NULL AFTER  `sync_direction` ,
ADD INDEX (  `take_in_sync` ,  `sync_direction` ) ;
CREATE TABLE IF NOT EXISTS `thermostats_progs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `thermostat_name` varchar(32) NOT NULL,
  `clima_status` varchar(32) NOT NULL,
  `day` enum('mon','tue','wed','thu','fri','sat','sun') NOT NULL DEFAULT 'mon',
  `position` int(11) unsigned NOT NULL DEFAULT '0',
  `h00` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h01` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h02` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h03` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h04` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h05` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h06` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h07` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h08` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h09` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h10` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h11` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h12` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h13` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h14` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h15` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h16` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h17` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h18` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h19` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h20` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h21` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h22` decimal(3,1) NOT NULL DEFAULT '20.0',
  `h23` decimal(3,1) NOT NULL DEFAULT '20.0',
  PRIMARY KEY (`id`),
  KEY `thermostat_name` (`thermostat_name`),
  KEY `clima_status` (`clima_status`,`day`),
  KEY `position` (`position`),
  KEY `active` (`day`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

ALTER TABLE `thermostats_progs`
  ADD CONSTRAINT `thermostats_progs_ibfk_1` FOREIGN KEY (`thermostat_name`) REFERENCES `thermostats` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;


CREATE TABLE IF NOT EXISTS `thermostats` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `button_name` varchar(255) NOT NULL,
  `position` int(10) unsigned NOT NULL,
  `sensor_type` enum('analog','digital','statuses','uniques') NOT NULL DEFAULT 'analog',
  `sensor_domain` varchar(32) NOT NULL DEFAULT '*',
  `function` enum('manual','program') NOT NULL DEFAULT 'manual',
  `minslide` decimal(3,1) NOT NULL DEFAULT '14.5',
  `maxslide` decimal(3,1) NOT NULL DEFAULT '40.0',
  `active` enum('yes','no') NOT NULL DEFAULT 'yes',
  `setval` decimal(3,1) NOT NULL DEFAULT '20.0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `active` (`active`),
  KEY `button_name` (`button_name`,`position`),
  KEY `function` (`function`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

