DROP table thermostats;
DROP table thermostats_progs;
DROP table thermostats_actions;
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
  `lastcheck` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastchange` decimal(13,2) NOT NULL DEFAULT '0.00',
  `temp_changed` tinyint(1) NOT NULL DEFAULT '0',
  `function_changed` tinyint(11) NOT NULL DEFAULT '0',
  `status_changed` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `active` (`active`),
  KEY `button_name` (`button_name`,`position`),
  KEY `function` (`function`),
  KEY `temp_changed` (`temp_changed`,`function_changed`,`status_changed`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

CREATE TABLE IF NOT EXISTS `thermostats_actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `thermostat_name` varchar(32) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `change_trigger` enum('any','function_change','status_change','temp_change') NOT NULL DEFAULT 'any',
  `thermostat_function` enum('any','manual','program') NOT NULL DEFAULT 'any',
  `clima_status` varchar(32) NOT NULL DEFAULT '*',
  `min_time` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `launch_sequence` enum('yes','no') NOT NULL DEFAULT 'no',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `use_command` enum('yes','no') NOT NULL DEFAULT 'no',
  `command` varchar(1024) NOT NULL,
  `ikapacket` tinyint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(32) DEFAULT 'Q.CLIMA',
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(11) DEFAULT NULL,
  `ikap_arg` varchar(1024) DEFAULT NULL,
  `ipdest` varchar(15) DEFAULT '255.255.255.255',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  `comment` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `status_name` (`thermostat_name`),
  KEY `active` (`active`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  KEY `clima_status` (`clima_status`),
  KEY `thermostat_function` (`thermostat_function`),
  KEY `trigger` (`change_trigger`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

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
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;
ALTER TABLE `thermostats_actions`
  ADD CONSTRAINT `thermostats_actions_ibfk_1` FOREIGN KEY (`thermostat_name`) REFERENCES `thermostats` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE `thermostats_progs`
  ADD CONSTRAINT `thermostats_progs_ibfk_1` FOREIGN KEY (`thermostat_name`) REFERENCES `thermostats` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;

DELIMITER ;;
CREATE TRIGGER thermostat_lastchange BEFORE UPDATE ON thermostats
   FOR EACH ROW
   BEGIN
      IF NOT (NEW.setval <=> OLD.setval AND NEW.function <=> OLD.function) THEN
         IF NEW.setval <> OLD.setval THEN
            SET NEW.temp_changed = 1;
         END IF;
         IF NEW.function <> OLD.function THEN
            SET NEW.function_changed = 1;
         END IF;
         IF EXISTS (SELECT 1 FROM mysql.func where name='microsecnow') THEN
            SET NEW.lastchange = MICROSECNOW()/1000000;
         ELSE
            SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
         END IF;
      END IF;
   END ;;
CREATE TRIGGER thermostatinsert_lastchange BEFORE INSERT ON thermostats
   FOR EACH ROW
   BEGIN
      SET NEW.temp_changed = 1;
      SET NEW.function_changed = 1;
      SET NEW.status_changed = 1;
      IF EXISTS (SELECT 1 FROM mysql.func where name='microsecnow') THEN
         SET NEW.lastchange = MICROSECNOW()/1000000;
      ELSE
         SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
      END IF;
   END ;;
DELIMITER ;
DROP TRIGGER config_lastchange;
DROP TRIGGER configinsert_lastchange;
DELIMITER ;;
CREATE TRIGGER config_lastchange BEFORE UPDATE ON daemon_config
   FOR EACH ROW
   BEGIN
      IF EXISTS (SELECT 1 FROM mysql.func where name='microsecnow') THEN
         SET NEW.lastchange = MICROSECNOW()/1000000;
      ELSE
         SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
      END IF;
   END ;;
CREATE TRIGGER configinsert_lastchange BEFORE INSERT ON daemon_config
   FOR EACH ROW
   BEGIN
     IF EXISTS (SELECT 1 FROM mysql.func where name='microsecnow') THEN
        SET NEW.lastchange = MICROSECNOW()/1000000;
     ELSE
        SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
     END IF;
   END ;;
DELIMITER ;

ALTER TABLE  `ioconf_analogs` ADD  `ananame` VARCHAR( 32 ) NOT NULL AFTER  `ananum` ,
ADD INDEX (  `ananame` ) ;
ALTER TABLE  `ioconf_inputs` ADD  `inpname` VARCHAR( 32 ) NOT NULL AFTER  `inpnum` ,
ADD INDEX (  `inpname` ) ;
ALTER TABLE  `ioconf_outputs` ADD  `outname` VARCHAR( 32 ) NOT NULL AFTER  `outnum` ,
ADD INDEX (  `outname` ) ;
ALTER TABLE  `status_actions` CHANGE  `ikap_act`  `ikap_act` INT( 11 ) NULL ;
ALTER TABLE  `voip_actions` CHANGE  `ikap_act`  `ikap_act` INT( 10 ) UNSIGNED NULL ;

