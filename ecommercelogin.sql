CREATE DATABASE IF NOT EXISTS `ecommercelogin` DEFAULT CHARACTER SET;
USE `ecommercelogin`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
)
alter table accounts add column address varchar(300) DEFAULT '';
alter table accounts add column zip int(11) DEFAULT 0;
alter table accounts add column zip2 varchar(20) DEFAULT '';

CREATE TABLE IF NOT EXISTS`images` (
  `file_name` int(11) NOT NULL AUTO_INCREMENT,
  `id` int(11) NOT NULL,
  `uploaded_on` varchar(255) NOT NULL,
  `file_type` varchar(255) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `title` varchar(55) NOT NULL,
  `description` varchar(300) NOT NULL,
  PRIMARY KEY (`file_name`)
)
alter table images add column merchantname varchar(100) DEFAULT '';
alter table images add column gateway varchar(50) DEFAULT '';
alter table images add column gatewaymerchantid varchar(200) DEFAULT '';

CREATE TABLE IF NOT EXISTS`cart` (
  `cartitemid` int(11) NOT NULL AUTO_INCREMENT,
  `file_address` varchar(255) NOT NULL,
  `id` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `title` varchar(55) NOT NULL,
  `description` varchar(300) NOT NULL,
  PRIMARY KEY (`cartitemid`)
)

CREATE TABLE IF NOT EXISTS`liked` (
  `likeditemid` int(11) NOT NULL AUTO_INCREMENT,
  `file_address` varchar(255) NOT NULL,
  `id` int(11) NOT NULL,
  `title` varchar(55) NOT NULL,
  `description` varchar(300) NOT NULL,
  `price` int(11) NOT NULL,
  PRIMARY KEY (`likeditemid`)
)
ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;