SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin_menu
-- ----------------------------
DROP TABLE IF EXISTS `admin_menu`;
CREATE TABLE `admin_menu` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `parent_id` bigint NOT NULL DEFAULT '0',
  `order` int NOT NULL DEFAULT '0',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `uri` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `extension` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `show` tinyint NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_menu
-- ----------------------------
BEGIN;
INSERT INTO `admin_menu` VALUES (1, 0, 1, 'Index', 'feather icon-bar-chart-2', '/', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (2, 0, 2, 'Admin', 'feather icon-settings', '', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (3, 2, 3, 'Users', '', 'auth/users', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (4, 2, 4, 'Roles', '', 'auth/roles', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (5, 2, 5, 'Permission', '', 'auth/permissions', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (6, 2, 6, 'Menu', '', 'auth/menu', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (7, 2, 7, 'Extensions', '', 'auth/extensions', '', 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_menu` VALUES (11, 0, 9, 'Goods_Manage', 'fa-shopping-bag', NULL, '', 1, '2021-05-16 11:39:55', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (12, 11, 11, 'Goods', 'fa-shopping-bag', '/goods', '', 1, '2021-05-16 11:44:35', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (13, 11, 10, 'Goods_Group', 'fa-star-half-o', '/goods-group', '', 1, '2021-05-16 17:08:43', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (14, 0, 12, 'Carmis_Manage', 'fa-credit-card-alt', NULL, '', 1, '2021-05-17 21:29:50', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (15, 14, 13, 'Carmis', 'fa-credit-card', '/carmis', '', 1, '2021-05-17 21:37:59', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (16, 14, 14, 'Import_Carmis', 'fa-plus-circle', '/import-carmis', '', 1, '2021-05-18 14:46:35', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (17, 18, 16, 'Coupon', 'fa-dollar', '/coupon', '', 1, '2021-05-18 17:29:53', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (18, 0, 15, 'Coupon_Manage', 'fa-diamond', NULL, '', 1, '2021-05-18 17:32:03', '2021-05-18 17:32:03');
INSERT INTO `admin_menu` VALUES (19, 0, 17, 'Configuration', 'fa-wrench', NULL, '', 1, '2021-05-20 20:06:47', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (20, 19, 18, 'Email_Template_Configuration', 'fa-envelope', '/emailtpl', '', 1, '2021-05-20 20:17:07', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (21, 19, 19, 'Pay_Configuration', 'fa-cc-visa', '/pay', '', 1, '2021-05-20 20:41:24', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (22, 0, 8, 'Order_Manage', 'fa-table', NULL, '', 1, '2021-05-23 20:43:43', '2021-05-23 20:44:20');
INSERT INTO `admin_menu` VALUES (23, 22, 20, 'Order', 'fa-heart', '/order', '', 1, '2021-05-23 20:46:13', '2021-05-23 20:47:16');
INSERT INTO `admin_menu` VALUES (24, 19, 21, 'System_Setting', 'fa-cogs', '/system-setting', '', 1, '2021-05-26 10:26:34', '2021-05-26 10:26:34');
INSERT INTO `admin_menu` VALUES (25, 19, 22, 'Email_Test', 'fa-envelope', '/email-test', '', 1, '2022-07-26 12:09:34', '2022-07-26 12:17:21');
INSERT INTO `admin_menu` VALUES (26, 19, 23, 'Banner', 'fa-image', '/banner', '', 1, '2026-06-06 00:00:00', NULL);
INSERT INTO `admin_menu` VALUES (27, 11, 12, 'Goods_SKU', 'fa-tags', '/goods-sku', '', 1, '2026-06-06 00:00:00', NULL);

COMMIT;

-- ----------------------------
-- Table structure for admin_permission_menu
-- ----------------------------
DROP TABLE IF EXISTS `admin_permission_menu`;
CREATE TABLE `admin_permission_menu` (
  `permission_id` bigint NOT NULL,
  `menu_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `admin_permission_menu_permission_id_menu_id_unique` (`permission_id`,`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_permission_menu
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for admin_permissions
-- ----------------------------
DROP TABLE IF EXISTS `admin_permissions`;
CREATE TABLE `admin_permissions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `http_method` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `http_path` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `order` int NOT NULL DEFAULT '0',
  `parent_id` bigint NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_permissions_slug_unique` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_permissions
-- ----------------------------
BEGIN;
INSERT INTO `admin_permissions` VALUES (1, 'Auth management', 'auth-management', '', '', 1, 0, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_permissions` VALUES (2, 'Users', 'users', '', '/auth/users*', 2, 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_permissions` VALUES (3, 'Roles', 'roles', '', '/auth/roles*', 3, 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_permissions` VALUES (4, 'Permissions', 'permissions', '', '/auth/permissions*', 4, 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_permissions` VALUES (5, 'Menu', 'menu', '', '/auth/menu*', 5, 1, '2021-05-16 02:06:08', NULL);
INSERT INTO `admin_permissions` VALUES (6, 'Extension', 'extension', '', '/auth/extensions*', 6, 1, '2021-05-16 02:06:08', NULL);
COMMIT;

-- ----------------------------
-- Table structure for admin_role_menu
-- ----------------------------
DROP TABLE IF EXISTS `admin_role_menu`;
CREATE TABLE `admin_role_menu` (
  `role_id` bigint NOT NULL,
  `menu_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `admin_role_menu_role_id_menu_id_unique` (`role_id`,`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_role_menu
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for admin_role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `admin_role_permissions`;
CREATE TABLE `admin_role_permissions` (
  `role_id` bigint NOT NULL,
  `permission_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `admin_role_permissions_role_id_permission_id_unique` (`role_id`,`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_role_permissions
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for admin_role_users
-- ----------------------------
DROP TABLE IF EXISTS `admin_role_users`;
CREATE TABLE `admin_role_users` (
  `role_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `admin_role_users_role_id_user_id_unique` (`role_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_role_users
-- ----------------------------
BEGIN;
INSERT INTO `admin_role_users` VALUES (1, 1, '2021-05-16 02:06:08', '2021-05-16 02:06:08');
COMMIT;

-- ----------------------------
-- Table structure for admin_roles
-- ----------------------------
DROP TABLE IF EXISTS `admin_roles`;
CREATE TABLE `admin_roles` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_roles_slug_unique` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_roles
-- ----------------------------
BEGIN;
INSERT INTO `admin_roles` VALUES (1, 'Administrator', 'administrator', '2021-05-16 02:06:08', '2021-05-16 02:06:08');
COMMIT;

-- ----------------------------
-- Table structure for admin_settings
-- ----------------------------
DROP TABLE IF EXISTS `admin_settings`;
CREATE TABLE `admin_settings` (
  `slug` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_settings
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for admin_users
-- ----------------------------
DROP TABLE IF EXISTS `admin_users`;
CREATE TABLE `admin_users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remember_token` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_users_username_unique` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of admin_users
-- ----------------------------
BEGIN;
INSERT INTO `admin_users` VALUES (1, 'admin', '$2y$10$e7z99Mhxm9BOHL55xHZTx.QcNTZJC6ftRXHCR/ZkBja/jBeasVeBy', 'Administrator', NULL, '4UAXF2BEw9EL1Tr2aGmwkv5DKwxqRF6djOMAHSiBMSOrPfPNHYrjCCQMtnTC', '2021-05-16 02:06:08', '2021-05-16 02:06:08');
COMMIT;

-- ----------------------------
-- ----------------------------
-- Table structure for banners
-- ----------------------------
DROP TABLE IF EXISTS `banners`;
CREATE TABLE `banners` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subtitle` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `button_text` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `link` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ord` int NOT NULL DEFAULT '1',
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ----------------------------
-- Records of banners
-- ----------------------------
BEGIN;
COMMIT;

-- Table structure for carmis
-- ----------------------------
DROP TABLE IF EXISTS `carmis`;
CREATE TABLE `carmis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `goods_id` int NOT NULL,
  `sku_id` int DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT '1',
  `is_loop` tinyint(1) NOT NULL DEFAULT '0',
  `carmi` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_goods_id` (`goods_id`) USING BTREE,
  KEY `idx_sku_id` (`sku_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of carmis
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for coupons
-- ----------------------------
DROP TABLE IF EXISTS `coupons`;
CREATE TABLE `coupons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `discount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `is_use` tinyint(1) NOT NULL DEFAULT '1',
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `coupon` varchar(150) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `ret` int NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_coupon` (`coupon`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of coupons
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for coupons_goods
-- ----------------------------
DROP TABLE IF EXISTS `coupons_goods`;
CREATE TABLE `coupons_goods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `goods_id` int NOT NULL,
  `coupons_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of coupons_goods
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for emailtpls
-- ----------------------------
DROP TABLE IF EXISTS `emailtpls`;
CREATE TABLE `emailtpls` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tpl_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tpl_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tpl_token` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mail_token` (`tpl_token`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of emailtpls
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for failed_jobs
-- ----------------------------
DROP TABLE IF EXISTS `failed_jobs`;
CREATE TABLE `failed_jobs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `connection` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `queue` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `payload` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `exception` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `failed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of failed_jobs
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for goods
-- ----------------------------
DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `gd_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `gd_description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `gd_keywords` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `picture` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `retail_price` decimal(10,2) DEFAULT '0.00',
  `actual_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `in_stock` int NOT NULL DEFAULT '0',
  `sales_volume` int DEFAULT '0',
  `ord` int DEFAULT '1',
  `buy_limit_num` int NOT NULL DEFAULT '0',
  `buy_prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `type` tinyint(1) NOT NULL DEFAULT '1',
  `wholesale_price_cnf` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `other_ipu_cnf` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `api_hook` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of goods
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for goods_group
-- ----------------------------
DROP TABLE IF EXISTS `goods_group`;
CREATE TABLE `goods_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_id` int NOT NULL DEFAULT '0',
  `gp_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `ord` int NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of goods_group
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- ----------------------------
-- Table structure for goods_skus
-- ----------------------------
DROP TABLE IF EXISTS `goods_skus`;
CREATE TABLE `goods_skus` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `goods_id` int NOT NULL,
  `sku_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku_code` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DEFAULT',
  `actual_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `picture` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `in_stock` int NOT NULL DEFAULT '0',
  `ord` int NOT NULL DEFAULT '1',
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `goods_skus_goods_id_sku_code_unique` (`goods_id`,`sku_code`),
  KEY `idx_goods_id` (`goods_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of goods_skus
-- ----------------------------
BEGIN;
COMMIT;

-- Table structure for migrations
-- ----------------------------
DROP TABLE IF EXISTS `migrations`;
CREATE TABLE `migrations` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `migration` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of migrations
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_sn` varchar(150) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `goods_id` int NOT NULL,
  `sku_id` int DEFAULT NULL,
  `coupon_id` int DEFAULT '0',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` tinyint(1) NOT NULL DEFAULT '1',
  `goods_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `buy_amount` int NOT NULL DEFAULT '1',
  `coupon_discount_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `wholesale_discount_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `actual_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `search_pwd` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
  `email` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `info` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `pay_id` int DEFAULT NULL,
  `buy_ip` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `trade_no` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
  `status` tinyint(1) NOT NULL DEFAULT '1',
  `coupon_ret_back` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_order_sn` (`order_sn`) USING BTREE,
  KEY `idx_goods_id` (`goods_id`) USING BTREE,
  KEY `idx_sku_id` (`sku_id`) USING BTREE,
  KEY `idex_email` (`email`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Records of orders
-- ----------------------------
BEGIN;
COMMIT;

-- ----------------------------
-- Table structure for pays
-- ----------------------------
DROP TABLE IF EXISTS `pays`;
CREATE TABLE `pays` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pay_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pay_check` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pay_method` tinyint(1) NOT NULL,
  `pay_client` tinyint(1) NOT NULL DEFAULT '1',
  `merchant_id` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `merchant_key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `merchant_pem` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pay_handleroute` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_open` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_pay_check` (`pay_check`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Records of pays
-- ----------------------------
BEGIN;
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
