DROP DATABASE IF EXISTS Cloud;
CREATE DATABASE Cloud;

USE Cloud;

DROP DATABASE IF EXISTS dashboard_domain;
DROP DATABASE IF EXISTS dashboard_datacenter;
DROP DATABASE IF EXISTS dashboard_node;

--
-- Create model Datacenter
--
CREATE TABLE `dashboard_datacenter` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(100) NOT NULL, `ip` varchar(15) NOT NULL);
--
-- Create model Node
--
CREATE TABLE `dashboard_node` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `ip` varchar(15) NOT NULL, `name` varchar(100) NOT NULL, `datacenter_id` bigint NULL);
--
-- Create model Domain
--
CREATE TABLE `dashboard_domain` (`UUID` uuid NOT NULL PRIMARY KEY, `id` integer NOT NULL, `name` varchar(100) NOT NULL, `status` varchar(10) NOT NULL, `max_ram` integer NOT NULL, `current_ram` integer NOT NULL, `vcpus` integer NOT NULL, `vnc_port` integer NULL, `proxy_port` integer NULL, `ip` varchar(15) NOT NULL, `node_id` bigint NULL);

ALTER TABLE `dashboard_node`   ADD CONSTRAINT `dashboard_node_datacenter_id_892245c1_fk_dashboard_datacenter_id` FOREIGN KEY (`datacenter_id`) REFERENCES `dashboard_datacenter` (`id`);
ALTER TABLE `dashboard_domain` ADD CONSTRAINT `dashboard_domain_node_id_53c47817_fk_dashboard_node_id`           FOREIGN KEY (`node_id`      ) REFERENCES `dashboard_node`       (`id`);

INSERT INTO `dashboard_datacenter` (id, name, ip) VALUES (1, 'moxprox', '192.168.20.24');
