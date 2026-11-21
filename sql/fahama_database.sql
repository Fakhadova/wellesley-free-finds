/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.19  Distrib 10.11.18-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: fahama_db
-- ------------------------------------------------------
-- Server version	10.11.18-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

USE fahama_db; 

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  `parent_cid` int(11) DEFAULT NULL,
  `comment` varchar(250) NOT NULL,
  `posted_at` datetime NOT NULL,
  PRIMARY KEY (`cid`),
  KEY `pid` (`pid`),
  KEY `uid` (`uid`),
  KEY `parent_cid` (`parent_cid`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `comments_ibfk_3` FOREIGN KEY (`parent_cid`) REFERENCES `comments` (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `interests`
--

DROP TABLE IF EXISTS `interests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `interests` (
  `iid` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  `status` enum('Pending','Accepted','Declined','Withdrawn','Closed') NOT NULL,
  PRIMARY KEY (`iid`),
  UNIQUE KEY `pid` (`pid`,`uid`),
  KEY `uid` (`uid`),
  CONSTRAINT `interests_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`),
  CONSTRAINT `interests_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `mid` int(11) NOT NULL AUTO_INCREMENT,
  `pid` int(11) NOT NULL,
  `sender_uid` int(11) NOT NULL,
  `recipient_uid` int(11) NOT NULL,
  `message` text NOT NULL,
  `sent_at` datetime NOT NULL,
  PRIMARY KEY (`mid`),
  KEY `pid` (`pid`),
  KEY `sender_uid` (`sender_uid`),
  KEY `recipient_uid` (`recipient_uid`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`recipient_uid`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES
(1,1,1,2,'Hi! When would you like to pick up the lamp?','2026-10-25 19:00:00'),
(2,1,2,1,'Would tomorrow afternoon work?','2026-10-25 19:05:00');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `nid` int(11) NOT NULL AUTO_INCREMENT,
  `recipient_uid` int(11) NOT NULL,
  `actor_uid` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `iid` int(11) DEFAULT NULL,
  `cid` int(11) DEFAULT NULL,
  `type` enum('NewRequest','NewOffer','Accepted','Declined','Withdrawn','Comment','Reply','StatusChange') NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`nid`),
  KEY `recipient_uid` (`recipient_uid`),
  KEY `actor_uid` (`actor_uid`),
  KEY `pid` (`pid`),
  KEY `iid` (`iid`),
  KEY `cid` (`cid`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`recipient_uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`actor_uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `notifications_ibfk_3` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`),
  CONSTRAINT `notifications_ibfk_4` FOREIGN KEY (`iid`) REFERENCES `interests` (`iid`),
  CONSTRAINT `notifications_ibfk_5` FOREIGN KEY (`cid`) REFERENCES `comments` (`cid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES
(1,2,1,1,1,NULL,'Accepted',0,'2026-10-25 18:40:00'),
(2,3,1,2,3,NULL,'NewOffer',0,'2026-10-25 18:45:00'),
(3,2,1,1,NULL,2,'Reply',0,'2026-10-25 18:15:00');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `pid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `post_type` enum('Donate','Request') NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `category` set('Clothing_Shoes','School_Supplies','Kitchenware','Books','Technology','Decorations_Furniture','Tools_Sporting_Goods','Miscellaneous') NOT NULL,
  `photo_filename` varchar(255) DEFAULT NULL,
  `status` enum('Available','Claimed','Completed','Open','Fulfilled') NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `posted_at` datetime NOT NULL,
  PRIMARY KEY (`pid`),
  KEY `uid` (`uid`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `picfile`;
CREATE TABLE `picfile` (
  `pid` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `mimetype` varchar(50) NOT NULL,
  `photo` mediumblob NOT NULL,
  PRIMARY KEY (`pid`),
  UNIQUE KEY `filename` (`filename`),
  CONSTRAINT `picfile_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


-- Table structure for table `saved_posts`
--

DROP TABLE IF EXISTS `saved_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `saved_posts` (
  `sid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  PRIMARY KEY (`sid`),
  UNIQUE KEY `uid` (`uid`,`pid`),
  KEY `pid` (`pid`),
  CONSTRAINT `saved_posts_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `saved_posts_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `posts` (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `email` varchar(50) DEFAULT NULL,
  `password_hash` varchar(255) not null,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 20:10:29
