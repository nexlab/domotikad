ALTER TABLE  `daemon_config` ADD  `lastchange` DECIMAL( 13, 2 ) NOT NULL DEFAULT  '0', ADD INDEX (  `lastchange` );
DELIMITER ;;
CREATE TRIGGER config_lastchange BEFORE UPDATE ON daemon_config
   FOR EACH ROW
   BEGIN
     SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
   END ;;
CREATE TRIGGER configinsert_lastchange BEFORE INSERT ON daemon_config
   FOR EACH ROW
   BEGIN
     SET NEW.lastchange = TIMESTAMPDIFF(second,'1970-01-01 01:00:00',NOW());
   END ;;
DELIMITER ;

