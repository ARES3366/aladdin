create database if not exists milvus;
use milvus;
CREATE TABLE if not exists `tbl_face_info` (
  `face_id` bigint(64) NOT NULL,
  `url` char(255) NOT NULL,
  `_left` int(11) NOT NULL,
  `_right` int(11) NOT NULL,
  `_top` int(11) NOT NULL,
  `_bottom` int(11) NOT NULL,
  `person_name` char(64) DEFAULT NULL,
  PRIMARY KEY (`face_id`),
  UNIQUE KEY `unique_url_left_top` (`url`,`_left`,`_top`),
  KEY `idx_person_name` (`person_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create database if not exists atf_db;
use atf_db;
CREATE TABLE IF NOT EXISTS `t_cls_file`
(
    `f_id` BIGINT(100) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
    `f_task_id` VARCHAR(100) NOT NULL COMMENT '任务id',
    `f_class` VARCHAR(100) NOT NULL COMMENT '此任务下的类别名称',
    `f_cls_simi` FLOAT NOT NULL COMMENT '此任务下的类别平均相似度',
    `f_file_name` VARCHAR(128) NOT NULL COMMENT '此类别下的文件名',
    `f_word` VARCHAR(1000) NOT NULL COMMENT '关键短语',
    `f_flag` VARCHAR(10) NOT NULL COMMENT '此文件是否参与类关键词提取标记',
    PRIMARY KEY (`f_id`),
    UNIQUE INDEX (`f_task_id`,`f_class`,`f_file_name`)
)
    ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE=utf8mb4_bin COMMENT = '任务id、类别、类别下文本表'; 
       
CREATE TABLE IF NOT EXISTS `t_cond`
(
    `f_id` BIGINT(100) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
    `f_cond_id` VARCHAR(100) NOT NULL COMMENT '条件id',
    `f_group_id` VARCHAR(100) NOT NULL COMMENT '条件分组id',
    `f_cond` VARCHAR(128) NOT NULL COMMENT '此条件名称',
    `f_file_name` VARCHAR(128) NOT NULL COMMENT '此类别下的文件名',
    `f_word` VARCHAR(600) NOT NULL COMMENT '关键短语',
    `f_milvusid` BIGINT NOT NULL COMMENT '向量数据存入milvus中返回的id',
    PRIMARY KEY (`f_id`),
    UNIQUE INDEX (`f_cond_id`,`f_file_name`)
)
    ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '条件文件表';
    
CREATE TABLE IF NOT EXISTS `t_group` 
(
    `f_id` BIGINT(100) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
    `f_group_id` VARCHAR (100) NOT NULL COMMENT '条件分组id',
    `f_group` VARCHAR (128) NOT NULL COMMENT '条件分组名称',
    PRIMARY KEY (`f_id`),
    UNIQUE INDEX (`f_group`)
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE=utf8mb4_bin COMMENT = '所有的条件分组表' ;