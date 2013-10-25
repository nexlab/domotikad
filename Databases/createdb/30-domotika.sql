-- MySQL dump 10.13  Distrib 5.5.33, for debian-linux-gnu (armv7l)
--
-- Host: localhost    Database: domotika
-- ------------------------------------------------------
-- Server version	5.5.33-1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `dynamic` tinyint(1) NOT NULL DEFAULT '0',
  `detected` tinyint(1) NOT NULL DEFAULT '0',
  `exact_dst` int(1) NOT NULL DEFAULT '0',
  `rcv_dst` varchar(255) NOT NULL,
  `rcv_msgtype` int(11) NOT NULL DEFAULT '0',
  `rcv_ctx` int(11) NOT NULL DEFAULT '0',
  `rcv_act` int(11) NOT NULL DEFAULT '0',
  `use_rcv_arg` int(11) NOT NULL DEFAULT '0',
  `rcv_arg` varchar(255) DEFAULT NULL,
  `execute` int(11) NOT NULL DEFAULT '0',
  `command` varchar(255) DEFAULT NULL,
  `ikapacket` int(11) NOT NULL DEFAULT '0',
  `ikap_src` varchar(255) NOT NULL DEFAULT 'Q.ACTION',
  `ikap_dst` varchar(255) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(11) DEFAULT NULL,
  `ikap_arg` varchar(255) DEFAULT NULL,
  `launch_sequence` int(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `local_only` int(11) NOT NULL DEFAULT '0',
  `active` int(11) NOT NULL DEFAULT '1',
  `position` int(11) NOT NULL DEFAULT '1',
  `ipdest` varchar(255) NOT NULL DEFAULT '255.255.255.255',
  `limit_run` int(11) NOT NULL DEFAULT '0',
  `run_count` int(11) NOT NULL DEFAULT '1',
  `min_time` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `status` varchar(255) DEFAULT NULL,
  `color_on` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'green',
  `color_off` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'gray',
  `text_on` varchar(10) NOT NULL DEFAULT 'ON',
  `text_off` varchar(10) NOT NULL DEFAULT 'OFF',
  `status2` varchar(255) DEFAULT NULL,
  `color2_on` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'azure',
  `color2_off` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'gray',
  `text2_on` varchar(10) NOT NULL DEFAULT 'on',
  `text2_off` varchar(10) NOT NULL DEFAULT 'off',
  `action_loop_enabled` int(1) NOT NULL DEFAULT '0',
  `action_loop_interval` decimal(12,0) unsigned NOT NULL DEFAULT '1',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  PRIMARY KEY (`id`),
  KEY `rcv_dst` (`rcv_dst`),
  KEY `rcv_msgtype` (`rcv_msgtype`),
  KEY `rcv_ctx` (`rcv_ctx`),
  KEY `rcv_act` (`rcv_act`),
  KEY `use_rcv_arg` (`use_rcv_arg`),
  KEY `rcv_arg` (`rcv_arg`),
  KEY `execute` (`execute`),
  KEY `command` (`command`),
  KEY `ikapacket` (`ikapacket`),
  KEY `ikap_src` (`ikap_src`),
  KEY `ikap_dst` (`ikap_dst`),
  KEY `ikap_msgtype` (`ikap_msgtype`),
  KEY `ikap_ctx` (`ikap_ctx`),
  KEY `ikap_act` (`ikap_act`),
  KEY `ikap_arg` (`ikap_arg`),
  KEY `sequence` (`launch_sequence`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `local_only` (`local_only`),
  KEY `active` (`active`),
  KEY `position` (`position`),
  KEY `ipdest` (`ipdest`),
  KEY `limit_run` (`limit_run`),
  KEY `run_count` (`run_count`),
  KEY `min_time` (`min_time`),
  KEY `last_run` (`lastrun`),
  KEY `status` (`status`),
  KEY `exact_dst` (`exact_dst`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  KEY `dynamic` (`dynamic`),
  KEY `detected` (`detected`),
  KEY `color_on` (`color_on`,`color_off`,`text_on`,`text_off`),
  KEY `status2` (`status2`,`color2_on`,`color2_off`,`text2_on`,`text2_off`),
  CONSTRAINT `actions_ibfk_1` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actions`
--

LOCK TABLES `actions` WRITE;
/*!40000 ALTER TABLE `actions` DISABLE KEYS */;
/*!40000 ALTER TABLE `actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `actstatus`
--

DROP TABLE IF EXISTS `actstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actstatus` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `buttonid` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '0',
  `status2` tinyint(4) NOT NULL DEFAULT '0',
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastchange` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `buttonid` (`buttonid`),
  KEY `status` (`status`),
  KEY `lastupdate` (`lastupdate`),
  KEY `lastchange` (`lastchange`),
  KEY `status2` (`status2`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actstatus`
--

LOCK TABLES `actstatus` WRITE;
/*!40000 ALTER TABLE `actstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `actstatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER actstatus_lastchange BEFORE UPDATE ON actstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status OR NEW.status2 <> OLD.status2 THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `analog`
--

DROP TABLE IF EXISTS `analog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analog` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `ananum` int(11) DEFAULT NULL,
  `dynamic` int(11) DEFAULT NULL,
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `active` int(11) NOT NULL DEFAULT '1',
  `position` int(11) DEFAULT '0',
  `ananame` varchar(255) DEFAULT NULL,
  `minval` int(11) NOT NULL DEFAULT '0',
  `maxval` int(11) NOT NULL DEFAULT '1023',
  `lowval` int(11) NOT NULL DEFAULT '256',
  `highval` int(11) NOT NULL DEFAULT '768',
  `color_min` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'blue',
  `color_low` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'green',
  `color_medium` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'orange',
  `color_high` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'red',
  `divider` float NOT NULL DEFAULT '1',
  `unit` varchar(10) NOT NULL DEFAULT 'VALUE',
  `detected` smallint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `inpnum` (`ananum`),
  KEY `dynamic` (`dynamic`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `active` (`active`),
  KEY `position` (`position`),
  KEY `inpname` (`ananame`),
  KEY `detected` (`detected`),
  KEY `minval` (`minval`,`maxval`),
  KEY `lowval` (`lowval`,`highval`),
  KEY `divider` (`divider`,`unit`),
  KEY `color_min` (`color_min`,`color_low`,`color_medium`,`color_high`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `analog`
--

LOCK TABLES `analog` WRITE;
/*!40000 ALTER TABLE `analog` DISABLE KEYS */;
/*!40000 ALTER TABLE `analog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `anastatus`
--

DROP TABLE IF EXISTS `anastatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `anastatus` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `buttonid` int(11) NOT NULL,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `ananum` int(11) DEFAULT NULL,
  `ananame` varchar(255) DEFAULT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastchange` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `buttonid` (`buttonid`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `inpnum` (`ananum`),
  KEY `inpname` (`ananame`),
  KEY `status` (`status`),
  KEY `lastupdate` (`lastupdate`),
  KEY `lastchange` (`lastchange`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `anastatus`
--

LOCK TABLES `anastatus` WRITE;
/*!40000 ALTER TABLE `anastatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `anastatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER anastatus_lastchange BEFORE UPDATE ON anastatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `bookmarks`
--

DROP TABLE IF EXISTS `bookmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bookmarks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `table_name` varchar(255) NOT NULL,
  `relstatus_buttonid` int(11) NOT NULL,
  `button_name` varchar(255) NOT NULL,
  `relnum` int(11) NOT NULL,
  `outnum` int(11) NOT NULL,
  `board_ip` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookmarks`
--

LOCK TABLES `bookmarks` WRITE;
/*!40000 ALTER TABLE `bookmarks` DISABLE KEYS */;
/*!40000 ALTER TABLE `bookmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daemon_config`
--

DROP TABLE IF EXISTS `daemon_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daemon_config` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `section` varchar(255) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `section` (`section`,`key`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daemon_config`
--

LOCK TABLES `daemon_config` WRITE;
/*!40000 ALTER TABLE `daemon_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `daemon_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dmboards`
--

DROP TABLE IF EXISTS `dmboards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dmboards` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `port` int(5) NOT NULL DEFAULT '6654',
  `transport` enum('UDP4','TCP4') NOT NULL DEFAULT 'UDP4',
  `webport` int(5) NOT NULL DEFAULT '80',
  `type` varchar(255) DEFAULT NULL,
  `fwtype` varchar(255) DEFAULT NULL,
  `fwversion` int(11) DEFAULT NULL,
  `last_status_request` decimal(13,2) NOT NULL DEFAULT '0.00',
  `last_status_update` decimal(13,2) NOT NULL DEFAULT '0.00',
  `detected` smallint(1) NOT NULL DEFAULT '1',
  `online` tinyint(1) NOT NULL DEFAULT '0',
  `confhash` varchar(255) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `ip` (`ip`),
  KEY `type` (`type`),
  KEY `fwtype` (`fwtype`),
  KEY `fwversion` (`fwversion`),
  KEY `last_status_update` (`last_status_update`),
  KEY `detected` (`detected`),
  KEY `confhash` (`confhash`),
  KEY `port` (`port`,`transport`),
  KEY `online` (`online`),
  KEY `last_status_request` (`last_status_request`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dmboards`
--

LOCK TABLES `dmboards` WRITE;
/*!40000 ALTER TABLE `dmboards` DISABLE KEYS */;
/*!40000 ALTER TABLE `dmboards` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email`
--

DROP TABLE IF EXISTS `email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `sender` varchar(255) NOT NULL,
  `to` varchar(255) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `message` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`,`sender`,`to`,`subject`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email`
--

LOCK TABLES `email` WRITE;
/*!40000 ALTER TABLE `email` DISABLE KEYS */;
/*!40000 ALTER TABLE `email` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_conf`
--

DROP TABLE IF EXISTS `email_conf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_conf` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `server` varchar(255) NOT NULL DEFAULT 'smtp.unixmedia.net',
  `port` int(5) NOT NULL DEFAULT '25',
  `use_auth` enum('true','false') NOT NULL DEFAULT 'true',
  `use_tls` enum('true','false') NOT NULL DEFAULT 'true',
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `server` (`server`,`port`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_conf`
--

LOCK TABLES `email_conf` WRITE;
/*!40000 ALTER TABLE `email_conf` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flags`
--

DROP TABLE IF EXISTS `flags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `flags` (
  `name` varchar(255) NOT NULL,
  `expire` decimal(13,2) DEFAULT NULL,
  UNIQUE KEY `name` (`name`),
  KEY `expire` (`expire`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flags`
--

LOCK TABLES `flags` WRITE;
/*!40000 ALTER TABLE `flags` DISABLE KEYS */;
/*!40000 ALTER TABLE `flags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `groupname` varchar(255) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`groupname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups_permissions`
--

DROP TABLE IF EXISTS `groups_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups_permissions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `groupname` varchar(255) NOT NULL,
  `permission_selector` enum('path','ikap') NOT NULL DEFAULT 'path',
  `permission_selection` varchar(512) NOT NULL,
  `permission_value` enum('r','w','rw') NOT NULL DEFAULT 'r',
  PRIMARY KEY (`id`),
  KEY `permission_selector` (`permission_selector`),
  KEY `permission_value` (`permission_value`),
  KEY `groupname` (`groupname`),
  CONSTRAINT `groups_permissions_ibfk_1` FOREIGN KEY (`groupname`) REFERENCES `groups` (`groupname`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups_permissions`
--

LOCK TABLES `groups_permissions` WRITE;
/*!40000 ALTER TABLE `groups_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `groups_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inpstatus`
--

DROP TABLE IF EXISTS `inpstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inpstatus` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `buttonid` int(11) NOT NULL,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `inpnum` int(11) DEFAULT NULL,
  `inpname` varchar(255) DEFAULT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastchange` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `buttonid` (`buttonid`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `inpnum` (`inpnum`),
  KEY `inpname` (`inpname`),
  KEY `status` (`status`),
  KEY `lastupdate` (`lastupdate`),
  KEY `lastchange` (`lastchange`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inpstatus`
--

LOCK TABLES `inpstatus` WRITE;
/*!40000 ALTER TABLE `inpstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `inpstatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER inpstatus_lastchange BEFORE UPDATE ON inpstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `input`
--

DROP TABLE IF EXISTS `input`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `input` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `inpnum` int(11) DEFAULT NULL,
  `dynamic` int(11) DEFAULT NULL,
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `active` int(11) NOT NULL DEFAULT '1',
  `position` int(11) DEFAULT '0',
  `inpname` varchar(255) DEFAULT NULL,
  `color_on` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'green',
  `color_off` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'orange',
  `text_on` varchar(10) NOT NULL DEFAULT 'CLOSE',
  `text_off` varchar(10) NOT NULL DEFAULT 'OPEN',
  `text_led` varchar(10) NOT NULL,
  `detected` smallint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `inpnum` (`inpnum`),
  KEY `dynamic` (`dynamic`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `active` (`active`),
  KEY `position` (`position`),
  KEY `inpname` (`inpname`),
  KEY `detected` (`detected`),
  KEY `color_on` (`color_on`,`color_off`,`text_on`,`text_off`),
  KEY `text_led` (`text_led`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `input`
--

LOCK TABLES `input` WRITE;
/*!40000 ALTER TABLE `input` DISABLE KEYS */;
/*!40000 ALTER TABLE `input` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `datetime` (`datetime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `motion_detection`
--

DROP TABLE IF EXISTS `motion_detection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `motion_detection` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `active` int(11) NOT NULL DEFAULT '1',
  `event_type` int(11) NOT NULL DEFAULT '1',
  `event_status` int(11) NOT NULL DEFAULT '1',
  `event_camera` varchar(255) NOT NULL,
  `event_zone` varchar(255) NOT NULL,
  `use_command` tinyint(1) NOT NULL DEFAULT '0',
  `command` varchar(255) NOT NULL,
  `ikapacket` tinyint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(255) NOT NULL DEFAULT 'Q.MOTION',
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_arg` varchar(1024) DEFAULT NULL,
  `ipdest` varchar(15) DEFAULT '255.255.255.255',
  `launch_sequence` tinyint(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `min_time` decimal(13,2) NOT NULL DEFAULT '1.00',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  `motion_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `active` (`active`),
  KEY `event_type` (`event_type`),
  KEY `event_status` (`event_status`),
  KEY `event_camera` (`event_camera`),
  KEY `event_zone` (`event_zone`),
  KEY `lastrun` (`lastrun`),
  KEY `limit_time` (`min_time`),
  KEY `min` (`min`),
  KEY `hour` (`hour`),
  KEY `day` (`day`),
  KEY `month` (`month`),
  KEY `dayofweek` (`dayofweek`),
  KEY `motion_name` (`motion_name`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  CONSTRAINT `motion_detection_ibfk_1` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `motion_detection`
--

LOCK TABLES `motion_detection` WRITE;
/*!40000 ALTER TABLE `motion_detection` DISABLE KEYS */;
/*!40000 ALTER TABLE `motion_detection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source` varchar(1024) NOT NULL DEFAULT 'action',
  `userdst` varchar(255) NOT NULL,
  `expire` decimal(13,2) NOT NULL,
  `readed` tinyint(1) NOT NULL DEFAULT '0',
  `message` varchar(1024) NOT NULL,
  `added` decimal(13,2) unsigned NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `userdst` (`userdst`,`expire`,`readed`),
  KEY `added` (`added`),
  KEY `source` (`source`(767))
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `output`
--

DROP TABLE IF EXISTS `output`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `output` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `outnum` int(11) DEFAULT NULL,
  `outtype` int(11) DEFAULT NULL,
  `ctx` int(11) DEFAULT NULL,
  `dynamic` int(11) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `has_relays` tinyint(1) NOT NULL DEFAULT '0',
  `has_pwms` tinyint(1) NOT NULL DEFAULT '0',
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `active` int(11) NOT NULL DEFAULT '1',
  `position` int(11) DEFAULT '0',
  `detected` smallint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `outnum` (`outnum`),
  KEY `outtype` (`outtype`),
  KEY `ctx` (`ctx`),
  KEY `dynamic` (`dynamic`),
  KEY `domain` (`domain`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `active` (`active`),
  KEY `position` (`position`),
  KEY `detected` (`detected`),
  KEY `has_relays` (`has_relays`,`has_pwms`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `output`
--

LOCK TABLES `output` WRITE;
/*!40000 ALTER TABLE `output` DISABLE KEYS */;
/*!40000 ALTER TABLE `output` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pwm`
--

DROP TABLE IF EXISTS `pwm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pwm` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `channel_name` varchar(255) NOT NULL,
  `detected` tinyint(1) NOT NULL DEFAULT '0',
  `dynamic` tinyint(1) NOT NULL DEFAULT '1',
  `websection` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `channel_name` (`channel_name`),
  KEY `detected` (`detected`,`dynamic`),
  KEY `websection` (`websection`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pwm`
--

LOCK TABLES `pwm` WRITE;
/*!40000 ALTER TABLE `pwm` DISABLE KEYS */;
/*!40000 ALTER TABLE `pwm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pwmstatus`
--

DROP TABLE IF EXISTS `pwmstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pwmstatus` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `pwmid` bigint(20) unsigned NOT NULL,
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `pwmid` (`pwmid`),
  KEY `lastupdate` (`lastupdate`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pwmstatus`
--

LOCK TABLES `pwmstatus` WRITE;
/*!40000 ALTER TABLE `pwmstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `pwmstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qservers`
--

DROP TABLE IF EXISTS `qservers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qservers` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  `mediaproxy` int(11) NOT NULL DEFAULT '1',
  `port` int(11) DEFAULT '443',
  `use_ssl` int(11) NOT NULL DEFAULT '1',
  `internal_media_only` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `host` (`host`),
  KEY `mediaproxy` (`mediaproxy`),
  KEY `port` (`port`),
  KEY `use_ssl` (`use_ssl`),
  KEY `internal_media_only` (`internal_media_only`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qservers`
--

LOCK TABLES `qservers` WRITE;
/*!40000 ALTER TABLE `qservers` DISABLE KEYS */;
/*!40000 ALTER TABLE `qservers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `relay`
--

DROP TABLE IF EXISTS `relay`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relay` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `outnum` int(11) DEFAULT NULL,
  `has_amp` tinyint(1) NOT NULL DEFAULT '0',
  `outtype` int(11) DEFAULT NULL,
  `ctx` int(11) DEFAULT NULL,
  `act` int(11) DEFAULT NULL,
  `msgtype` int(11) DEFAULT NULL,
  `dynamic` int(11) DEFAULT NULL,
  `relnum` int(11) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `color_on` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'green',
  `color_off` enum('gray','blue','azure','green','red','orange') NOT NULL DEFAULT 'gray',
  `text_on` varchar(10) NOT NULL DEFAULT 'ON',
  `text_off` varchar(10) NOT NULL DEFAULT 'OFF',
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `active` int(11) NOT NULL DEFAULT '1',
  `position` int(11) DEFAULT '0',
  `detected` smallint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `outnum` (`outnum`),
  KEY `outtype` (`outtype`),
  KEY `ctx` (`ctx`),
  KEY `act` (`act`),
  KEY `msgtype` (`msgtype`),
  KEY `dynamic` (`dynamic`),
  KEY `relnum` (`relnum`),
  KEY `domain` (`domain`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `active` (`active`),
  KEY `position` (`position`),
  KEY `detected` (`detected`),
  KEY `color_on` (`color_on`,`color_off`,`text_on`,`text_off`),
  KEY `has_amp` (`has_amp`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relay`
--

LOCK TABLES `relay` WRITE;
/*!40000 ALTER TABLE `relay` DISABLE KEYS */;
/*!40000 ALTER TABLE `relay` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `relstatus`
--

DROP TABLE IF EXISTS `relstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relstatus` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `buttonid` int(11) NOT NULL,
  `board_name` varchar(255) NOT NULL,
  `board_ip` varchar(255) DEFAULT NULL,
  `outnum` int(11) DEFAULT NULL,
  `ctx` int(11) DEFAULT NULL,
  `outtype` int(11) DEFAULT NULL,
  `relnum` int(11) DEFAULT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `ampere` int(3) unsigned NOT NULL DEFAULT '0',
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastchange` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `buttonid` (`buttonid`),
  KEY `board_name` (`board_name`),
  KEY `board_ip` (`board_ip`),
  KEY `outnum` (`outnum`),
  KEY `ctx` (`ctx`),
  KEY `outtype` (`outtype`),
  KEY `relnum` (`relnum`),
  KEY `status` (`status`),
  KEY `lastupdate` (`lastupdate`),
  KEY `ampere` (`ampere`),
  KEY `lastchange` (`lastchange`)
) ENGINE=MEMORY DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relstatus`
--

LOCK TABLES `relstatus` WRITE;
/*!40000 ALTER TABLE `relstatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `relstatus` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER relstatus_lastchange BEFORE UPDATE ON relstatus
   FOR EACH ROW
   BEGIN
      IF NEW.status <> OLD.status OR NEW.ampere <> OLD.ampere THEN
         SET NEW.lastchange = NEW.lastupdate;
      END IF;
   END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `sequence_conf`
--

DROP TABLE IF EXISTS `sequence_conf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sequence_conf` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `type` int(11) NOT NULL DEFAULT '0',
  `running` int(11) NOT NULL DEFAULT '0',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `description` varchar(255) DEFAULT NULL,
  `min_time` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `type` (`type`),
  KEY `running` (`running`),
  KEY `lastrun` (`lastrun`),
  KEY `min_time` (`min_time`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sequence_conf`
--

LOCK TABLES `sequence_conf` WRITE;
/*!40000 ALTER TABLE `sequence_conf` DISABLE KEYS */;
/*!40000 ALTER TABLE `sequence_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sequence_data`
--

DROP TABLE IF EXISTS `sequence_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sequence_data` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `sequence_name` varchar(255) NOT NULL,
  `execute` int(11) NOT NULL DEFAULT '0',
  `command` varchar(255) DEFAULT NULL,
  `ikapacket` int(11) NOT NULL DEFAULT '0',
  `ikap_src` varchar(255) NOT NULL DEFAULT 'Q.SEQUENCE',
  `ikap_dst` varchar(255) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(11) DEFAULT NULL,
  `ikap_arg` varchar(255) DEFAULT NULL,
  `launch_sequence` int(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `step_done` int(11) NOT NULL DEFAULT '0',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `time_next` decimal(13,2) NOT NULL DEFAULT '0.10',
  `position` int(11) NOT NULL DEFAULT '1',
  `ipdest` varchar(15) DEFAULT '255.255.255.255',
  `use_condition` int(11) NOT NULL DEFAULT '0',
  `condition` varchar(1024) NOT NULL,
  `condition_act` enum('GOTOSTEP','GOTOSEQ','STOP','RESTART','EXECUTEIF','NEXT','IGNORE') NOT NULL DEFAULT 'EXECUTEIF',
  `condition_actvalue` varchar(1024) NOT NULL,
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  PRIMARY KEY (`id`),
  KEY `execute` (`execute`),
  KEY `command` (`command`),
  KEY `ikapacket` (`ikapacket`),
  KEY `ikap_src` (`ikap_src`),
  KEY `ikap_dst` (`ikap_dst`),
  KEY `ikap_msgtype` (`ikap_msgtype`),
  KEY `ikap_ctx` (`ikap_ctx`),
  KEY `ikap_act` (`ikap_act`),
  KEY `ikap_arg` (`ikap_arg`),
  KEY `sequence` (`launch_sequence`),
  KEY `step_done` (`step_done`),
  KEY `last_done` (`lastrun`),
  KEY `time_next` (`time_next`),
  KEY `position` (`position`),
  KEY `ipdest` (`ipdest`),
  KEY `use_condition` (`use_condition`),
  KEY `condition_act` (`condition_act`),
  KEY `condition_seqid` (`condition_actvalue`(767)),
  KEY `sequence_name` (`sequence_name`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  CONSTRAINT `sequence_data_ibfk_1` FOREIGN KEY (`sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sequence_data_ibfk_2` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sequence_data`
--

LOCK TABLES `sequence_data` WRITE;
/*!40000 ALTER TABLE `sequence_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `sequence_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `speech_actions`
--

DROP TABLE IF EXISTS `speech_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `speech_actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `speechaction_name` varchar(255) DEFAULT NULL,
  `speech_string` varchar(255) NOT NULL,
  `active` smallint(1) NOT NULL DEFAULT '1',
  `use_command` int(1) NOT NULL DEFAULT '0',
  `command` varchar(255) DEFAULT NULL,
  `ikapacket` smallint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(255) NOT NULL DEFAULT 'Q.SPEECH',
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_arg` varchar(255) DEFAULT NULL,
  `ipdest` varchar(15) NOT NULL DEFAULT '255.255.255.255',
  `launch_sequence` int(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `ok_text2speech` varchar(255) NOT NULL DEFAULT 'Ok',
  `ko_text2speech` varchar(255) NOT NULL DEFAULT 'errore',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `min_time` decimal(13,2) NOT NULL DEFAULT '1.00',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  PRIMARY KEY (`id`),
  UNIQUE KEY `speechaction_name` (`speechaction_name`),
  KEY `active` (`active`),
  KEY `event_camera` (`use_command`),
  KEY `event_zone` (`command`),
  KEY `lastrun` (`lastrun`),
  KEY `limit_time` (`min_time`),
  KEY `min` (`min`),
  KEY `hour` (`hour`),
  KEY `day` (`day`),
  KEY `month` (`month`),
  KEY `dayofweek` (`dayofweek`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  KEY `speech_string` (`speech_string`),
  CONSTRAINT `speech_actions_ibfk_1` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `speech_actions`
--

LOCK TABLES `speech_actions` WRITE;
/*!40000 ALTER TABLE `speech_actions` DISABLE KEYS */;
/*!40000 ALTER TABLE `speech_actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats_charts`
--

DROP TABLE IF EXISTS `stats_charts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats_charts` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `title` text NOT NULL,
  `grid_background` varchar(255) NOT NULL DEFAULT 'rgba(0,0,0,0)',
  `grid_shadow` enum('true','false') NOT NULL DEFAULT 'false',
  `grid_border` enum('true','false') NOT NULL DEFAULT 'false',
  `legend_show` enum('true','false') NOT NULL DEFAULT 'true',
  `legend_position` enum('w','nw','n','ne','e','se','s','sw') NOT NULL DEFAULT 'nw',
  `legend_placement` enum('outside','insideGrid') NOT NULL DEFAULT 'insideGrid',
  `y_label_precision` smallint(5) unsigned NOT NULL DEFAULT '0',
  `x_formatString` varchar(64) DEFAULT NULL,
  `y_formatString` varchar(64) DEFAULT NULL,
  `x_numberTicks` int(10) unsigned DEFAULT NULL,
  `y_numberTicks` int(10) unsigned DEFAULT NULL,
  `websection` varchar(256) NOT NULL DEFAULT 'home',
  `webposition` int(1) NOT NULL DEFAULT '1',
  `active` int(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `websection` (`websection`,`webposition`,`active`),
  KEY `grid_shadow` (`grid_shadow`,`grid_border`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats_charts`
--

LOCK TABLES `stats_charts` WRITE;
/*!40000 ALTER TABLE `stats_charts` DISABLE KEYS */;
INSERT INTO `stats_charts` VALUES (1,'tempo_rele_luci_e_prese','Tempo rele\' chiusi totale in minuti giornaliero','rgba(0,0,0,0)','false','false','true','nw','insideGrid',0,NULL,NULL,7,NULL,'home',5,1),(2,'consumi_totali','Consumi ultime 24 ore','rgba(0,0,0,0)','false','false','true','nw','insideGrid',2,NULL,NULL,NULL,NULL,'home',1,1),(3,'consumi_totali_week','Consumi (media oraria) ultima settimana','rgba(0,0,0,0)','false','false','true','nw','insideGrid',2,NULL,NULL,7,NULL,'home',3,1),(4,'Utilizzo_utenze','Prese attive e luci accese ultime 24 ore','rgba(0,0,0,0)','false','false','true','nw','insideGrid',2,NULL,NULL,NULL,NULL,'home',2,1);
/*!40000 ALTER TABLE `stats_charts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats_charts_series`
--

DROP TABLE IF EXISTS `stats_charts_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats_charts_series` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `active` enum('1','0') NOT NULL DEFAULT '1',
  `selector_type` enum('SQL','script','file','daily_sum','hourly_sum') NOT NULL DEFAULT 'SQL',
  `selector_subtype` enum('back_in_time','limits') NOT NULL DEFAULT 'back_in_time',
  `selector_start` datetime DEFAULT NULL,
  `selector_stop` datetime DEFAULT NULL,
  `selector_numopt` int(11) NOT NULL DEFAULT '1',
  `selector_name` varchar(512) NOT NULL,
  `x_coefficient` enum('equal','divider','moltiplier') NOT NULL DEFAULT 'equal',
  `x_coefficient_val` float NOT NULL DEFAULT '0',
  `y_coefficient` enum('equal','divider','moltiplier') NOT NULL DEFAULT 'equal',
  `y_coefficient_val` float NOT NULL DEFAULT '0',
  `label` varchar(512) NOT NULL,
  `marker_style` enum('filledSquare','filledCircle','circle','square') NOT NULL DEFAULT 'filledCircle',
  `marker_show` enum('true','false') NOT NULL DEFAULT 'true',
  `marker_size` tinyint(4) NOT NULL DEFAULT '8',
  `color` varchar(512) DEFAULT NULL,
  `highlighter_formatString` varchar(255) NOT NULL DEFAULT '%s, %d',
  `fill` enum('true','false') NOT NULL DEFAULT 'true',
  `line_width` tinyint(4) NOT NULL DEFAULT '4',
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `active` (`active`),
  KEY `selector_subtype` (`selector_subtype`,`selector_start`,`selector_stop`),
  CONSTRAINT `stats_charts_series_ibfk_1` FOREIGN KEY (`name`) REFERENCES `stats_charts` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats_charts_series`
--

LOCK TABLES `stats_charts_series` WRITE;
/*!40000 ALTER TABLE `stats_charts_series` DISABLE KEYS */;
INSERT INTO `stats_charts_series` VALUES (1,'tempo_rele_luci_e_prese','1','daily_sum','back_in_time',NULL,NULL,7,'prese_tempo_accese_min','equal',0,'equal',0,'rele\' prese','filledSquare','true',8,'rgba(220,220,220,0.7)','%s, %d','true',4),(2,'tempo_rele_luci_e_prese','1','daily_sum','back_in_time',NULL,NULL,7,'luci_tempo_accese_min','equal',0,'equal',0,'rele\' luci','filledCircle','true',8,'rgba(151,187,205,0.7)','%s, %d','true',4),(3,'consumi_totali','1','SQL','back_in_time',NULL,NULL,7,'select datetime as x, data as y from stats_data where name=\'amperaggio_totale_5min\' and datetime>=DATE_ADD(NOW(), INTERVAL -1 DAY)','equal',0,'equal',0,'Ampere','filledCircle','false',8,'rgba(220,220,220,0.7)','%s, %.2f','true',2),(4,'consumi_totali','1','SQL','back_in_time',NULL,NULL,7,'select datetime as x, data*0.23 as y from stats_data where name=\'amperaggio_totale_5min\' and datetime>=DATE_ADD(NOW(), INTERVAL -1 DAY)','equal',0,'equal',0,'kW','filledSquare','false',8,'rgba(151,187,205,0.7)','%s, %.2f','true',2),(5,'consumi_totali_week','1','hourly_sum','back_in_time',NULL,NULL,7,'amperaggio_media_oraria','equal',0,'equal',0,'Amperaggio media oraria','filledCircle','false',8,'rgba(220,220,220,0.7)','%s, %.2f','true',2),(6,'consumi_totali_week','1','hourly_sum','back_in_time',NULL,NULL,7,'amperaggio_media_oraria','equal',0,'moltiplier',0.23,'kW/h','filledSquare','false',8,'rgba(151,187,205,0.7)','%s, %.2f','true',2),(7,'Utilizzo_utenze','1','SQL','back_in_time',NULL,NULL,7,'select datetime as x, data as y from stats_data where name=\'prese_attive_5min\' and datetime>=DATE_ADD(NOW(), INTERVAL -1 DAY)','equal',0,'equal',0,'Prese in carico','filledCircle','false',8,'rgba(200,50,50,1)','%s, %d','false',1),(8,'Utilizzo_utenze','1','SQL','back_in_time',NULL,NULL,7,'select datetime as x, data as y from stats_data where name=\'luci_accese_5min\' and datetime>=DATE_ADD(NOW(), INTERVAL -1 DAY)','equal',0,'equal',0,'Luci Accese','filledCircle','false',8,'rgba(50,200,50,1)','%s, %d','false',1);
/*!40000 ALTER TABLE `stats_charts_series` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats_conf`
--

DROP TABLE IF EXISTS `stats_conf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats_conf` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `stats_type` enum('realtime','history') NOT NULL DEFAULT 'realtime',
  `selector` varchar(2048) NOT NULL,
  `interval` int(10) unsigned NOT NULL DEFAULT '5',
  `expire` bigint(20) unsigned NOT NULL DEFAULT '2880',
  `lastupdate` decimal(13,2) unsigned NOT NULL DEFAULT '0.00',
  `comment` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `active` (`active`),
  KEY `stats_type` (`stats_type`),
  KEY `interval` (`interval`),
  KEY `expire` (`expire`),
  KEY `lastupdate` (`lastupdate`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats_conf`
--

LOCK TABLES `stats_conf` WRITE;
/*!40000 ALTER TABLE `stats_conf` DISABLE KEYS */;
INSERT INTO `stats_conf` VALUES (1,'luci_accese_5min',1,'realtime','SQLCOUNT:select * from relstatus where status=1 and ctx=1 group by board_ip,outnum',5,2880,1382713630.00,'Controlla ogni 5 minuti quante luci sono accese in casa.'),(2,'prese_accese_5min',1,'realtime','SQLCOUNT:select * from relstatus where status=1 and ctx=2 group by board_ip,outnum',5,2880,1382713630.00,'Controlla ogni 5 minuti quante prese sono accese'),(3,'luci_tempo_accese_min',1,'history','SQL:SELECT SUM(data)*5 from stats_data WHERE name=\"luci_accese_5min\" AND datetime>=CONCAT(CURDATE(),\" \",HOUR(CURTIME()),\":00:00\") AND datetime<=CONCAT(CURDATE(),\" \",HOUR(CURTIME()),\":59:59\")',5,5256000,1382713630.00,'Conta il tempo totale delle accensioni di luci, mantiene il log per 10 anni'),(4,'prese_tempo_accese_min',1,'history','SQL:SELECT SUM(data)*5 from stats_data WHERE name=\"prese_accese_5min\" AND datetime>=CONCAT(CURDATE(),\" \",HOUR(CURTIME()),\":00:00\") AND datetime<=CONCAT(CURDATE(),\" \",HOUR(CURTIME()),\":59:59\")',5,5256000,1382713630.00,'Conta il tempo totale di accensione rele\', tiene i log per 10 anni'),(5,'amperaggio_totale_5min',1,'realtime','SQL:select SUM(f.ampere)/10 FROM (select ampere from relstatus as r where r.status=1 and ampere>5 group by r.board_ip,r.outnum) as f;',5,2880,1382713630.00,'Controlla ogni 5 minuti il consumo totale in ampere'),(6,'amperaggio_media_oraria',1,'history','SQL:select AVG(data) from stats_data as d where d.name=\'amperaggio_totale_5min\' and d.datetime>=DATE_FORMAT(NOW(), \'%Y-%m-%d %H\');',5,2880,1382713630.00,'ricava l\'amperaggio medio su base oraria'),(7,'prese_attive_5min',1,'realtime','SQLCOUNT:select * from relstatus where status=1 and ctx=2 and ampere>5 group by board_ip,outnum',5,2880,1382713630.00,'Controlla ogni 5 minuti quante prese sono attive con carico');
/*!40000 ALTER TABLE `stats_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats_data`
--

DROP TABLE IF EXISTS `stats_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats_data` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `datetime` datetime NOT NULL,
  `data` float NOT NULL,
  `txtdata` varchar(1024) NOT NULL,
  `lastupdate` decimal(13,2) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `lastupdate` (`lastupdate`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats_data`
--

LOCK TABLES `stats_data` WRITE;
/*!40000 ALTER TABLE `stats_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats_history`
--

DROP TABLE IF EXISTS `stats_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats_history` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `h00` float NOT NULL DEFAULT '0',
  `h01` float NOT NULL DEFAULT '0',
  `h02` float NOT NULL DEFAULT '0',
  `h03` float NOT NULL DEFAULT '0',
  `h04` float NOT NULL DEFAULT '0',
  `h05` float NOT NULL DEFAULT '0',
  `h06` float NOT NULL DEFAULT '0',
  `h07` float NOT NULL DEFAULT '0',
  `h08` float NOT NULL DEFAULT '0',
  `h09` float NOT NULL DEFAULT '0',
  `h10` float NOT NULL DEFAULT '0',
  `h11` float NOT NULL DEFAULT '0',
  `h12` float NOT NULL DEFAULT '0',
  `h13` float NOT NULL DEFAULT '0',
  `h14` float NOT NULL DEFAULT '0',
  `h15` float NOT NULL DEFAULT '0',
  `h16` float NOT NULL DEFAULT '0',
  `h17` float NOT NULL DEFAULT '0',
  `h18` float NOT NULL DEFAULT '0',
  `h19` float NOT NULL DEFAULT '0',
  `h20` float NOT NULL DEFAULT '0',
  `h21` float NOT NULL DEFAULT '0',
  `h22` float NOT NULL DEFAULT '0',
  `h23` float NOT NULL DEFAULT '0',
  `lastupdate` decimal(13,2) unsigned NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `date` (`date`),
  KEY `lastupdate` (`lastupdate`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats_history`
--

LOCK TABLES `stats_history` WRITE;
/*!40000 ALTER TABLE `stats_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `stats_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status_actions`
--

DROP TABLE IF EXISTS `status_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status_actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `status_name` varchar(255) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `action_type` enum('onchange','continous') NOT NULL DEFAULT 'onchange',
  `selector` enum('=','>','<','>=','<=','!=','domain') NOT NULL DEFAULT 'domain',
  `value` varchar(1024) NOT NULL,
  `retard` decimal(13,2) NOT NULL DEFAULT '0.00',
  `min_time` decimal(13,2) NOT NULL DEFAULT '0.00',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `launch_sequence` enum('yes','no') NOT NULL DEFAULT 'no',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `use_command` enum('yes','no') NOT NULL DEFAULT 'no',
  `command` varchar(1024) NOT NULL,
  `ikapacket` tinyint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(32) DEFAULT 'Q.STATUSES',
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(11) NOT NULL,
  `ikap_arg` varchar(1024) DEFAULT NULL,
  `ipdest` varchar(15) DEFAULT '255.255.255.255',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  `comment` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `status_name` (`status_name`),
  KEY `active` (`active`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  CONSTRAINT `status_actions_ibfk_1` FOREIGN KEY (`status_name`) REFERENCES `statuses` (`status_name`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `status_actions_ibfk_2` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status_actions`
--

LOCK TABLES `status_actions` WRITE;
/*!40000 ALTER TABLE `status_actions` DISABLE KEYS */;
/*!40000 ALTER TABLE `status_actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statuses` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `status_name` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `trigger` varchar(1024) NOT NULL,
  `trigger_interval` decimal(13,2) NOT NULL DEFAULT '300.00',
  `lastconfig` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `status_name` (`status_name`),
  KEY `lastconfig` (`lastconfig`),
  KEY `active` (`active`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statuses`
--

LOCK TABLES `statuses` WRITE;
/*!40000 ALTER TABLE `statuses` DISABLE KEYS */;
INSERT INTO `statuses` VALUES (1,'day.civil',1,'DAYCIVIL',1.00,'2013-09-21 12:00:57'),(2,'day.real',1,'DAYREAL',1.00,'2013-09-21 12:00:57'),(3,'day.max',1,'DAYMAX',1.00,'2013-09-21 12:01:27'),(4,'day.astro',1,'DAYASTRO',1.00,'2013-09-21 12:01:27');
/*!40000 ALTER TABLE `statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statusrealtime`
--

DROP TABLE IF EXISTS `statusrealtime`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statusrealtime` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `status_name` varchar(255) NOT NULL,
  `value` varchar(1024) NOT NULL,
  `lastupdate` decimal(13,2) NOT NULL,
  `lastchange` decimal(13,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `status_name` (`status_name`),
  KEY `value` (`value`)
) ENGINE=MEMORY AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statusrealtime`
--

LOCK TABLES `statusrealtime` WRITE;
/*!40000 ALTER TABLE `statusrealtime` DISABLE KEYS */;
/*!40000 ALTER TABLE `statusrealtime` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timers`
--

DROP TABLE IF EXISTS `timers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `timers` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `active` int(11) NOT NULL DEFAULT '1',
  `fromyear` int(11) DEFAULT NULL,
  `toyear` int(11) DEFAULT NULL,
  `use_command` tinyint(1) NOT NULL DEFAULT '0',
  `command` varchar(255) NOT NULL,
  `ikapacket` tinyint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(32) DEFAULT NULL,
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(11) DEFAULT NULL,
  `ikap_arg` varchar(1024) DEFAULT NULL,
  `ipdest` varchar(15) DEFAULT NULL,
  `launch_sequence` tinyint(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `lastrun` decimal(13,2) DEFAULT NULL,
  `limit_run` int(11) NOT NULL DEFAULT '0',
  `run_count` int(11) NOT NULL DEFAULT '1',
  `jump_next` int(11) NOT NULL DEFAULT '0',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  `timer_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `active` (`active`),
  KEY `fromyear` (`fromyear`),
  KEY `toyear` (`toyear`),
  KEY `lastrun` (`lastrun`),
  KEY `limit_run` (`limit_run`),
  KEY `run_count` (`run_count`),
  KEY `jump_next` (`jump_next`),
  KEY `min` (`min`),
  KEY `hour` (`hour`),
  KEY `day` (`day`),
  KEY `month` (`month`),
  KEY `dayofweek` (`dayofweek`),
  KEY `timer_name` (`timer_name`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  KEY `ikap_act` (`ikap_act`),
  CONSTRAINT `timers_ibfk_1` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timers`
--

LOCK TABLES `timers` WRITE;
/*!40000 ALTER TABLE `timers` DISABLE KEYS */;
/*!40000 ALTER TABLE `timers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uniques`
--

DROP TABLE IF EXISTS `uniques`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uniques` (
  `name` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  `lastupdate` decimal(13,2) NOT NULL DEFAULT '0.00',
  UNIQUE KEY `name` (`name`),
  KEY `lastupdate` (`lastupdate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uniques`
--

LOCK TABLES `uniques` WRITE;
/*!40000 ALTER TABLE `uniques` DISABLE KEYS */;
/*!40000 ALTER TABLE `uniques` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_gui_bookmarks`
--

DROP TABLE IF EXISTS `user_gui_bookmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_gui_bookmarks` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `bookmark_name` varchar(32) NOT NULL DEFAULT 'bookmarks',
  `bookmark_content` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user` (`user`),
  KEY `bookmark_name` (`bookmark_name`),
  CONSTRAINT `user_gui_bookmarks_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_gui_bookmarks`
--

LOCK TABLES `user_gui_bookmarks` WRITE;
/*!40000 ALTER TABLE `user_gui_bookmarks` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_gui_bookmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_gui_macrobuttons`
--

DROP TABLE IF EXISTS `user_gui_macrobuttons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_gui_macrobuttons` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `macrobutton_name` varchar(32) NOT NULL,
  `macrobutton_type` enum('link','rest-GET','rest-POST','rest-PUT','rest-DELETE') NOT NULL DEFAULT 'link',
  `uri` varchar(1024) NOT NULL,
  `text` varchar(1024) NOT NULL,
  `image` varchar(1024) NOT NULL,
  `rgbcolor` varchar(20) NOT NULL,
  `width` varchar(10) NOT NULL,
  `height` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user` (`user`),
  KEY `macrobutton_name` (`macrobutton_name`,`macrobutton_type`,`uri`(767),`text`(767)),
  CONSTRAINT `user_gui_macrobuttons_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_gui_macrobuttons`
--

LOCK TABLES `user_gui_macrobuttons` WRITE;
/*!40000 ALTER TABLE `user_gui_macrobuttons` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_gui_macrobuttons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_gui_panels`
--

DROP TABLE IF EXISTS `user_gui_panels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_gui_panels` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `page` enum('actuations','video','cameras') NOT NULL DEFAULT 'actuations',
  `panel_title` varchar(1024) NOT NULL,
  `panel_type` enum('standard','macrobuttons','bookmarks','cameras','video') NOT NULL DEFAULT 'standard',
  `panel_cols` enum('1','2','3','4','5','6','7','8','9','10','11','12') NOT NULL DEFAULT '1',
  `panel_height` varchar(11) NOT NULL DEFAULT '200',
  `panel_visible` enum('all','visible-sm','visible-md','visible-lg','hidden-sm','hidden-md','hidden-lg') NOT NULL DEFAULT 'all',
  `panel_position` int(11) NOT NULL DEFAULT '1',
  `panel_sections` varchar(1024) NOT NULL DEFAULT '*',
  `panel_websections` varchar(1024) NOT NULL DEFAULT '*',
  `panel_selector` enum('dmdomain') NOT NULL DEFAULT 'dmdomain',
  `panel_content` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user` (`user`),
  KEY `panel_title` (`panel_title`(767),`panel_type`,`panel_cols`,`panel_height`,`panel_position`),
  KEY `page` (`page`),
  CONSTRAINT `user_gui_panels_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_gui_panels`
--

LOCK TABLES `user_gui_panels` WRITE;
/*!40000 ALTER TABLE `user_gui_panels` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_gui_panels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `passwd` varchar(255) NOT NULL,
  `language` enum('it','en') NOT NULL DEFAULT 'en',
  `active` int(1) NOT NULL DEFAULT '1',
  `email` varchar(255) NOT NULL,
  `homepath` varchar(1024) NOT NULL DEFAULT '/domotika/',
  `desktop_homepath` varchar(1024) NOT NULL DEFAULT '/domotika/gui',
  `mobile_homepath` varchar(1024) NOT NULL DEFAULT '/domotika/gui',
  `default_permissions` enum('none','r','w','rw') NOT NULL DEFAULT 'none',
  `tts` tinyint(1) NOT NULL DEFAULT '1',
  `last_update` decimal(13,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `passwd` (`passwd`),
  KEY `active` (`active`),
  KEY `language` (`language`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','e9d355b67c790954d5d73db705f741b5c7f16c35','en',1,'','/domotika/','/domotika/gui','/domotika/gui','rw',1,1379027026.40);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_groups` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `groupname` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `username` (`username`),
  KEY `groupname` (`groupname`),
  CONSTRAINT `users_groups_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `users_groups_ibfk_2` FOREIGN KEY (`groupname`) REFERENCES `groups` (`groupname`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_permissions`
--

DROP TABLE IF EXISTS `users_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users_permissions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `permission_selector` enum('path','ikap') NOT NULL DEFAULT 'path',
  `permission_selection` varchar(512) NOT NULL,
  `permission_value` enum('r','w','rw') NOT NULL DEFAULT 'r',
  PRIMARY KEY (`id`),
  KEY `username` (`username`),
  KEY `permission_selector` (`permission_selector`),
  KEY `permission_value` (`permission_value`),
  CONSTRAINT `users_permissions_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_permissions`
--

LOCK TABLES `users_permissions` WRITE;
/*!40000 ALTER TABLE `users_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video`
--

DROP TABLE IF EXISTS `video`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `video` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) DEFAULT NULL,
  `controlapi` varchar(1024) DEFAULT NULL,
  `videostream` varchar(1024) DEFAULT NULL,
  `force_input_codec` varchar(32) NOT NULL,
  `audiostream` varchar(1024) DEFAULT NULL,
  `mjpeg` varchar(1024) DEFAULT NULL,
  `multicast` varchar(255) DEFAULT NULL,
  `multicast_id` varchar(255) DEFAULT NULL,
  `manufacturer` varchar(255) DEFAULT NULL,
  `model` varchar(255) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `websection` varchar(255) DEFAULT NULL,
  `button_name` varchar(255) DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `active` int(11) DEFAULT '1',
  `screenshot` varchar(1024) DEFAULT NULL,
  `dynamic` int(11) NOT NULL DEFAULT '1',
  `upnp_location` varchar(255) DEFAULT NULL,
  `has_ptz` enum('yes','no') NOT NULL DEFAULT 'no',
  `has_zoom` enum('yes','no') NOT NULL DEFAULT 'no',
  `has_preset` enum('yes','no') NOT NULL DEFAULT 'no',
  `has_channels` enum('yes','no') NOT NULL DEFAULT 'no',
  PRIMARY KEY (`id`),
  KEY `ip` (`ip`(1)),
  KEY `audiovideo_uri_high` (`videostream`(767)),
  KEY `audio_uri_high` (`audiostream`(767)),
  KEY `mjpeg_high` (`mjpeg`(767)),
  KEY `multicast` (`multicast`),
  KEY `multicast_id` (`multicast_id`),
  KEY `manufacturer` (`manufacturer`),
  KEY `model` (`model`),
  KEY `version` (`version`),
  KEY `websection` (`websection`),
  KEY `button_name` (`button_name`),
  KEY `position` (`position`),
  KEY `active` (`active`),
  KEY `screenshot_high` (`screenshot`(767)),
  KEY `dynamic` (`dynamic`),
  KEY `upnp_location` (`upnp_location`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `video`
--

LOCK TABLES `video` WRITE;
/*!40000 ALTER TABLE `video` DISABLE KEYS */;
/*!40000 ALTER TABLE `video` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_actions`
--

DROP TABLE IF EXISTS `voip_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_actions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `voipaction_name` varchar(255) DEFAULT NULL,
  `active` smallint(1) NOT NULL DEFAULT '1',
  `extension` varchar(255) DEFAULT NULL,
  `context_dmdomain` varchar(32) NOT NULL DEFAULT '*',
  `use_command` int(1) NOT NULL DEFAULT '0',
  `command` varchar(255) DEFAULT NULL,
  `ikapacket` tinyint(1) NOT NULL DEFAULT '0',
  `ikap_src` varchar(255) NOT NULL DEFAULT 'Q.VOIP',
  `ikap_dst` varchar(32) DEFAULT NULL,
  `ikap_msgtype` int(11) DEFAULT NULL,
  `ikap_ctx` int(11) DEFAULT NULL,
  `ikap_act` int(10) unsigned NOT NULL,
  `ikap_arg` varchar(1024) DEFAULT NULL,
  `ipdest` varchar(15) DEFAULT '255.255.255.255',
  `launch_sequence` int(1) NOT NULL DEFAULT '0',
  `launch_sequence_name` varchar(255) DEFAULT NULL,
  `ok_text2speech` varchar(255) NOT NULL DEFAULT 'Eseguito',
  `ko_text2speech` varchar(255) NOT NULL DEFAULT 'Errore',
  `menu_id` int(11) NOT NULL DEFAULT '0',
  `menu_text2speech` varchar(1024) NOT NULL,
  `menu_position` int(11) NOT NULL DEFAULT '1',
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `min_time` decimal(13,2) NOT NULL DEFAULT '1.00',
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  PRIMARY KEY (`id`),
  KEY `active` (`active`),
  KEY `event_type` (`extension`),
  KEY `event_status` (`context_dmdomain`),
  KEY `event_camera` (`use_command`),
  KEY `event_zone` (`command`),
  KEY `lastrun` (`lastrun`),
  KEY `limit_time` (`min_time`),
  KEY `min` (`min`),
  KEY `hour` (`hour`),
  KEY `day` (`day`),
  KEY `month` (`month`),
  KEY `dayofweek` (`dayofweek`),
  KEY `motion_name` (`voipaction_name`),
  KEY `launch_sequence_name` (`launch_sequence_name`),
  KEY `ikap_act` (`ikap_act`),
  CONSTRAINT `voip_actions_ibfk_1` FOREIGN KEY (`launch_sequence_name`) REFERENCES `sequence_conf` (`name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_actions`
--

LOCK TABLES `voip_actions` WRITE;
/*!40000 ALTER TABLE `voip_actions` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_aliases`
--

DROP TABLE IF EXISTS `voip_aliases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_aliases` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` smallint(1) NOT NULL DEFAULT '1',
  `extension` varchar(255) NOT NULL,
  `context_dmdomain` varchar(32) NOT NULL DEFAULT '*',
  `aliasto` varchar(255) NOT NULL,
  `contextto` varchar(255) NOT NULL DEFAULT 'domotika_users',
  `launch_voipaction` enum('yes','no') NOT NULL DEFAULT 'no',
  `voip_action_name` varchar(255) DEFAULT NULL,
  `min` varchar(255) NOT NULL DEFAULT '*',
  `hour` varchar(255) NOT NULL DEFAULT '*',
  `day` varchar(255) NOT NULL DEFAULT '*',
  `month` varchar(255) NOT NULL DEFAULT '*',
  `dayofweek` varchar(255) NOT NULL DEFAULT '*',
  PRIMARY KEY (`id`),
  KEY `active` (`active`,`extension`,`context_dmdomain`,`aliasto`),
  KEY `contextto` (`contextto`),
  KEY `voip_action_name` (`voip_action_name`),
  KEY `min` (`min`,`hour`,`day`,`month`,`dayofweek`),
  CONSTRAINT `voip_aliases_ibfk_1` FOREIGN KEY (`voip_action_name`) REFERENCES `voip_actions` (`voipaction_name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_aliases`
--

LOCK TABLES `voip_aliases` WRITE;
/*!40000 ALTER TABLE `voip_aliases` DISABLE KEYS */;
INSERT INTO `voip_aliases` VALUES (21,1,'280','*','all','domotika_queue','no',NULL,'*','*','*','*','*'),(22,1,'in','domotika_in','all','domotika_queue','no',NULL,'*','*','*','*','*'),(23,1,'281','*','domotika_speechrec','domotika_internal','no',NULL,'*','*','*','*','*');
/*!40000 ALTER TABLE `voip_aliases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_dialplan`
--

DROP TABLE IF EXISTS `voip_dialplan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_dialplan` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `position` int(11) unsigned NOT NULL DEFAULT '1',
  `context` varchar(255) NOT NULL DEFAULT 'domotika_trunk',
  `extension` varchar(255) NOT NULL DEFAULT 's',
  `priority` varchar(32) NOT NULL DEFAULT 'n',
  `astcommand` varchar(512) NOT NULL DEFAULT 'Hangup()',
  PRIMARY KEY (`id`),
  KEY `position` (`position`,`context`,`extension`,`priority`)
) ENGINE=InnoDB AUTO_INCREMENT=318 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_dialplan`
--

LOCK TABLES `voip_dialplan` WRITE;
/*!40000 ALTER TABLE `voip_dialplan` DISABLE KEYS */;
INSERT INTO `voip_dialplan` VALUES (5,3,'domotika_trunk','_7XX','1','Goto(parkedcalls,${EXTEN},1)'),(26,1,'domotika_users','_X.','2','Dial(SIP/${EXTEN},${TIMEOUT_USERS},rtTwWkKh)'),(27,2,'domotika_users','_X.','3','Hangup()'),(28,3,'domotika_users','_[a-z].','2','Dial(SIP/${EXTEN},${TIMEOUT_USERS},rtTwWkKh)'),(29,4,'domotika_users','_[a-z].','2','Hangup()'),(30,5,'domotika_users','_[A-Z].','2','Dial(SIP/${EXTEN},${TIMEOUT_USERS},rtTwWkKh)'),(31,6,'domotika_users','_[A-Z].','2','Hangup()'),(73,1,'domotika_out','_[A-Z].','1','Dial(SIP/pstn/${EXTEN},,r)'),(74,2,'domotika_out','_[A-Z].','n','Hangup()'),(75,3,'domotika_out','_[a-z].','1','Dial(SIP/pstn/${EXTEN},,r)'),(76,4,'domotika_out','_[a-z].','n','Hangup()'),(77,5,'domotika_out','_X.','1','Dial(SIP/pstn/${EXTEN},,r)'),(78,6,'domotika_out','_X.','n','Hangup()'),(103,1,'domotika_internal','_222','1','Answer()'),(104,2,'domotika_internal','_222','2','Echo()'),(105,3,'domotika_internal','_223','1','Answer()'),(106,4,'domotika_internal','_223','2','Record(/tmp/prova:sln,3,15)'),(107,5,'domotika_internal','_X.','1','AGI(agi://${AGIHOST}:${AGIPORT}/internal)'),(108,6,'domotika_internal','_X.','n','Goto(domotika_out,${EXTEN},1)'),(109,7,'domotika_internal','_[a-z].','1','AGI(agi://${AGIHOST}:${AGIPORT}/internal)'),(110,8,'domotika_internal','_[a-z].','n','Goto(domotika_out,${EXTEN},1)'),(111,9,'domotika_internal','_[A-Z].','1','AGI(agi://${AGIHOST}:${AGIPORT}/internal)'),(112,10,'domotika_internal','_[A-Z].','n','Goto(domotika_out,${EXTEN},1)'),(285,1,'domotika_in','_X.','1','Goto(domotika_in,in,1)'),(286,2,'domotika_in','_[a-z].','1','Goto(domotika_in,in,1)'),(287,3,'domotika_in','_[A-Z].','1','Goto(domotika_in,in,1)'),(288,4,'domotika_in','in','1','Answer()'),(289,5,'domotika_in','in','n','Wait(2)'),(290,6,'domotika_in','in','n','Verbose(${CALLERID(DNID)})'),(291,7,'domotika_in','in','n','Verbose(${CALLERID(ANI-all)})'),(292,8,'domotika_in','in','n','Verbose(${CALLERID(ANI-tag)})'),(293,9,'domotika_in','in','n','Verbose(${CALLERID(ANI-num-plan)})'),(294,10,'domotika_in','in','n','Verbose(${CALLERID(subaddr)})'),(295,11,'domotika_in','in','n','Set(CALLERID(name-pres)=allowed)'),(296,12,'domotika_in','in','n','Set(CALLERID(name)=PSTNLine)'),(297,13,'domotika_in','in','n','Set(CALLERID(ANI-name-pres)=allowed)'),(298,14,'domotika_in','in','n','Set(CALLERID(ANI-name)=PSTNLine)'),(299,15,'domotika_in','in','n','Set(CALLERID(subaddr)=PSTNLine)'),(300,16,'domotika_in','in','n','AGI(agi://${AGIHOST}:${AGIPORT}/in)'),(301,17,'domotika_in','in','n','Hangup()'),(302,18,'domotika_in','s','1','Hangup()'),(303,19,'domotika_in','t','1','Hangup()'),(304,20,'domotika_in','r','1','Hangup()'),(305,21,'domotika_in','i','1','Hangup()'),(312,1,'domotika_queue','_X.','1','Queue(${EXTENTION},rtTwWckx,,,${TIMEOUT_USERS})'),(313,2,'domotika_queue','_X.','2','Hangup()'),(314,3,'domotika_queue','_[a-z].','1','Queue(${EXTEN},rtTwWckx,,,${TIMEOUT_USERS})'),(315,4,'domotika_queue','_[a-z].','2','Hangup()'),(316,5,'domotika_queue','_[A-Z].','1','Queue(${EXTEN},rtTwWckx,,,${TIMEOUT_USERS})'),(317,6,'domotika_queue','_[A-Z].','2','Hangup()');
/*!40000 ALTER TABLE `voip_dialplan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_events`
--

DROP TABLE IF EXISTS `voip_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_events` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `active` enum('yes','no') NOT NULL DEFAULT 'yes',
  `event_type` enum('dtmf-sent','dtmf-received') NOT NULL DEFAULT 'dtmf-sent',
  `caller` varchar(255) NOT NULL DEFAULT '*',
  `called` varchar(255) NOT NULL DEFAULT '*',
  `context` varchar(32) NOT NULL DEFAULT '*',
  `variable` varchar(255) NOT NULL,
  `voip_action_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `event_type` (`event_type`,`caller`,`called`),
  KEY `active` (`active`),
  KEY `voip_action_name` (`voip_action_name`),
  KEY `context` (`context`),
  CONSTRAINT `voip_events_ibfk_1` FOREIGN KEY (`voip_action_name`) REFERENCES `voip_actions` (`voipaction_name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_events`
--

LOCK TABLES `voip_events` WRITE;
/*!40000 ALTER TABLE `voip_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_menu`
--

DROP TABLE IF EXISTS `voip_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_menu` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `active` int(1) NOT NULL DEFAULT '1',
  `extension` varchar(255) NOT NULL,
  `context` varchar(255) NOT NULL DEFAULT 'domotika_menus',
  `menu_pin` int(11) NOT NULL,
  `lastrun` decimal(13,2) NOT NULL DEFAULT '0.00',
  `menu_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_menu`
--

LOCK TABLES `voip_menu` WRITE;
/*!40000 ALTER TABLE `voip_menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_queue`
--

DROP TABLE IF EXISTS `voip_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_queue` (
  `name` varchar(128) NOT NULL,
  `musiconhold` varchar(128) DEFAULT NULL,
  `announce` varchar(128) DEFAULT NULL,
  `context` varchar(128) DEFAULT NULL,
  `timeout` int(11) DEFAULT '60',
  `monitor_join` tinyint(1) DEFAULT NULL,
  `monitor_format` varchar(128) DEFAULT NULL,
  `queue_youarenext` varchar(128) DEFAULT NULL,
  `queue_thereare` varchar(128) DEFAULT NULL,
  `queue_callswaiting` varchar(128) DEFAULT NULL,
  `queue_holdtime` varchar(128) DEFAULT NULL,
  `queue_minutes` varchar(128) DEFAULT NULL,
  `queue_seconds` varchar(128) DEFAULT NULL,
  `queue_lessthan` varchar(128) DEFAULT NULL,
  `queue_thankyou` varchar(128) DEFAULT NULL,
  `queue_reporthold` varchar(128) DEFAULT NULL,
  `announce_frequency` int(11) DEFAULT NULL,
  `announce_round_seconds` int(11) DEFAULT NULL,
  `announce_holdtime` varchar(128) DEFAULT NULL,
  `retry` int(11) DEFAULT NULL,
  `wrapuptime` int(11) DEFAULT NULL,
  `maxlen` int(11) DEFAULT NULL,
  `servicelevel` int(11) DEFAULT NULL,
  `strategy` varchar(128) DEFAULT NULL,
  `joinempty` varchar(128) DEFAULT NULL,
  `leavewhenempty` varchar(128) DEFAULT NULL,
  `eventmemberstatus` tinyint(1) DEFAULT NULL,
  `eventwhencalled` tinyint(1) DEFAULT NULL,
  `reportholdtime` tinyint(1) DEFAULT NULL,
  `memberdelay` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `timeoutrestart` tinyint(1) DEFAULT NULL,
  `periodic_announce` varchar(50) DEFAULT NULL,
  `periodic_announce_frequency` int(11) DEFAULT NULL,
  `ringinuse` tinyint(1) DEFAULT NULL,
  `setinterfacevar` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_queue`
--

LOCK TABLES `voip_queue` WRITE;
/*!40000 ALTER TABLE `voip_queue` DISABLE KEYS */;
INSERT INTO `voip_queue` VALUES ('all',NULL,NULL,NULL,60,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `voip_queue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_queue_members`
--

DROP TABLE IF EXISTS `voip_queue_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_queue_members` (
  `uniqueid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `membername` varchar(40) DEFAULT NULL,
  `queue_name` varchar(128) DEFAULT NULL,
  `interface` varchar(128) DEFAULT NULL,
  `penalty` int(11) DEFAULT NULL,
  `paused` int(11) DEFAULT NULL,
  PRIMARY KEY (`uniqueid`),
  UNIQUE KEY `queue_interface` (`queue_name`,`interface`),
  KEY `queue_name` (`queue_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_queue_members`
--

LOCK TABLES `voip_queue_members` WRITE;
/*!40000 ALTER TABLE `voip_queue_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_queue_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_register`
--

DROP TABLE IF EXISTS `voip_register`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_register` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `transport` enum('udp','tcp','tls') NOT NULL DEFAULT 'udp',
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `host` varchar(255) NOT NULL,
  `port` int(5) NOT NULL DEFAULT '5060',
  `number` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_register`
--

LOCK TABLES `voip_register` WRITE;
/*!40000 ALTER TABLE `voip_register` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_register` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_trunks`
--

DROP TABLE IF EXISTS `voip_trunks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_trunks` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `active` int(1) NOT NULL DEFAULT '1',
  `name` varchar(255) NOT NULL,
  `type` enum('friend','peer','user') NOT NULL DEFAULT 'friend',
  `username` varchar(255) DEFAULT NULL,
  `secret` varchar(255) DEFAULT NULL,
  `context` varchar(255) NOT NULL DEFAULT 'domotika_internal',
  `host` varchar(255) DEFAULT 'dynamic',
  `qualify` enum('yes','no') DEFAULT 'yes',
  `disallow` varchar(255) DEFAULT 'all',
  `allow` varchar(255) DEFAULT 'ulaw,h263p,h264,h263',
  `nat` enum('yes','no','force_rport','comedia') NOT NULL DEFAULT 'yes',
  `faxdetect` enum('yes','no','cng','t38') NOT NULL DEFAULT 'no',
  `transport` varchar(32) DEFAULT 'udp',
  `insecure` varchar(32) DEFAULT NULL,
  `videosupport` enum('yes','no','always') NOT NULL DEFAULT 'yes',
  `regexten` varchar(80) DEFAULT NULL,
  `realm` varchar(255) DEFAULT NULL,
  `srvlookup` enum('yes','no') NOT NULL DEFAULT 'yes',
  `canreinvite` enum('yes','no') NOT NULL DEFAULT 'yes',
  `fromuser` varchar(255) DEFAULT NULL,
  `fromdomain` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `active` (`active`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_trunks`
--

LOCK TABLES `voip_trunks` WRITE;
/*!40000 ALTER TABLE `voip_trunks` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_trunks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `voip_users`
--

DROP TABLE IF EXISTS `voip_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `voip_users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` enum('friend','peer','user') NOT NULL DEFAULT 'friend',
  `username` varchar(255) DEFAULT NULL,
  `secret` varchar(255) DEFAULT NULL,
  `context` varchar(255) NOT NULL DEFAULT 'domotika_internal',
  `host` varchar(255) DEFAULT 'dynamic',
  `qualify` enum('yes','no') DEFAULT 'yes',
  `disallow` varchar(255) DEFAULT 'all',
  `allow` varchar(255) DEFAULT 'ulaw,h263p,h264,h263',
  `callerid` varchar(255) DEFAULT NULL,
  `ipaddr` varchar(15) DEFAULT NULL,
  `port` mediumint(5) NOT NULL DEFAULT '0',
  `defaultip` varchar(15) DEFAULT NULL,
  `nat` enum('yes','no','force_rport','comedia') NOT NULL DEFAULT 'yes',
  `faxdetect` enum('yes','no','cng','t38') NOT NULL DEFAULT 'no',
  `transport` varchar(32) DEFAULT 'udp',
  `insecure` varchar(32) DEFAULT NULL,
  `regseconds` int(11) NOT NULL DEFAULT '0',
  `useragent` varchar(255) NOT NULL,
  `lastms` int(11) NOT NULL,
  `fullcontact` varchar(255) NOT NULL,
  `videosupport` enum('yes','no','always') NOT NULL DEFAULT 'yes',
  `regexten` varchar(80) DEFAULT NULL,
  `realm` varchar(255) DEFAULT NULL,
  `srvlookup` enum('yes','no') NOT NULL DEFAULT 'yes',
  `canreinvite` enum('yes','no') NOT NULL DEFAULT 'yes',
  `fromuser` varchar(255) DEFAULT NULL,
  `fromdomain` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `voip_users`
--

LOCK TABLES `voip_users` WRITE;
/*!40000 ALTER TABLE `voip_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `voip_users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-10-25 17:10:35
