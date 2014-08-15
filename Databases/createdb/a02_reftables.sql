CREATE TABLE IF NOT EXISTS `ref_ika_ctx` (
  `id` int(5) NOT NULL COMMENT 'IKA Context ID',
  `name` varchar(255) NOT NULL COMMENT 'IKA Context name'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='IKA reference: context names';

CREATE TABLE IF NOT EXISTS `ref_ika_msg` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='IKA reference: message types';

CREATE TABLE IF NOT EXISTS `ref_ika_act` (
  `id` int(11) NOT NULL,
  `nome` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='IKA reference: action names';
ALTER TABLE `ref_ika_act`
 ADD PRIMARY KEY (`id`);
ALTER TABLE `ref_ika_ctx`
 ADD PRIMARY KEY (`id`);
ALTER TABLE `ref_ika_msg`
 ADD PRIMARY KEY (`id`);


ALTER TABLE  `voip_actions` ADD INDEX (  `ikap_dst` ) ;
ALTER TABLE  `voip_actions` ADD INDEX (  `ikap_ctx` ) ;
ALTER TABLE  `voip_actions` ADD INDEX (  `ikap_act` ) ;
ALTER TABLE  `voip_actions` ADD INDEX (  `ikap_msgtype` ) ;
ALTER TABLE  `voip_actions` CHANGE  `ikap_act`  `ikap_act` INT( 11 ) NULL DEFAULT NULL ;

INSERT INTO `ref_ika_act` (`id`, `nome`) VALUES
(0, 'NULL'),
(1, 'on'),
(2, 'off'),
(3, 'change'),
(4, 'open'),
(5, 'close'),
(6, 'up'),
(7, 'down'),
(8, 'stop'),
(9, 'start'),
(10, 'stop timered'),
(11, 'start timered'),
(12, 'block unblock'),
(13, 'block'),
(14, 'unblock'),
(15, 'high'),
(16, 'low'),
(17, 'equal'),
(18, 'expired'),
(19, 'timedout'),
(20, 'changed'),
(21, 'switched on'),
(22, 'switched off'),
(23, 'call'),
(24, 'answer'),
(25, 'ring'),
(26, 'play'),
(27, 'pause'),
(28, 'pause closing'),
(29, 'pause opening'),
(30, 'next'),
(31, 'closing'),
(32, 'opening'),
(253, 'board'),
(255, 'debug');


INSERT INTO `ref_ika_ctx` (`id`, `name`) VALUES
(0, 'NULL'),
(1, 'light'),
(2, 'socket'),
(3, 'blind'),
(4, 'sensor'),
(5, 'door'),
(6, 'window'),
(7, 'valve'),
(8, 'status'),
(9, 'scenary'),
(10, 'alarm'),
(11, 'citophone'),
(12, 'generic switch'),
(13, 'thermostat'),
(14, 'gate'),
(15, 'audio'),
(16, 'video'),
(17, 'phone'),
(18, 'tv'),
(19, 'irrigation'),
(20, 'timer'),
(21, 'internet'),
(22, 'message'),
(23, 'rfid'),
(24, 'pump'),
(25, 'motor'),
(26, 'tent'),
(32, 'real time clock'),
(33, 'sequence'),
(65534, 'system'),
(65535, 'user');


INSERT INTO `ref_ika_msg` (`id`, `name`) VALUES
(0, 'NULL'),
(1, 'request'),
(2, 'action'),
(3, 'ack'),
(4, 'notify'),
(5, 'notifyconf'),
(6, 'requestconf'),
(7, 'setconf'),
(255, 'debug');


ALTER TABLE `actions`
ADD CONSTRAINT `actions_ibfk_2` FOREIGN KEY (`rcv_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `actions_ibfk_3` FOREIGN KEY (`ikap_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `actions_ibfk_4` FOREIGN KEY (`rcv_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `actions_ibfk_5` FOREIGN KEY (`ikap_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `actions_ibfk_6` FOREIGN KEY (`rcv_msgtype`) REFERENCES `ref_ika_msg` (`id`),
ADD CONSTRAINT `actions_ibfk_7` FOREIGN KEY (`ikap_msgtype`) REFERENCES `ref_ika_msg` (`id`);

ALTER TABLE `sequence_data`
ADD CONSTRAINT `sequence_data_ibfk_3` FOREIGN KEY (`ikap_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `sequence_data_ibfk_4` FOREIGN KEY (`ikap_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `sequence_data_ibfk_5` FOREIGN KEY (`ikap_msgtype`) REFERENCES `ref_ika_msg` (`id`);

ALTER TABLE `status_actions`
ADD CONSTRAINT `status_actions_ibfk_3` FOREIGN KEY (`ikap_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `status_actions_ibfk_4` FOREIGN KEY (`ikap_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `status_actions_ibfk_5` FOREIGN KEY (`ikap_msgtype`) REFERENCES `ref_ika_msg` (`id`);

ALTER TABLE `thermostats_actions`
ADD CONSTRAINT `thermostats_actions_ibfk_2` FOREIGN KEY (`ikap_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `thermostats_actions_ibfk_3` FOREIGN KEY (`ikap_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `thermostats_actions_ibfk_4` FOREIGN KEY (`ikap_msgtype`) REFERENCES `ref_ika_msg` (`id`);

ALTER TABLE `voip_actions`
ADD CONSTRAINT `voip_actions_ibfk_2` FOREIGN KEY (`ikap_ctx`) REFERENCES `ref_ika_ctx` (`id`),
ADD CONSTRAINT `voip_actions_ibfk_3` FOREIGN KEY (`ikap_act`) REFERENCES `ref_ika_act` (`id`),
ADD CONSTRAINT `voip_actions_ibfk_4` FOREIGN KEY (`ikap_msgtype`) REFERENCES `ref_ika_msg` (`id`);





