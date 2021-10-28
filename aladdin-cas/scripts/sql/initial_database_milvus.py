import pymysql

sql='''
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8
'''

db_conn = pymysql.connect(host='aladdin-cas-mysql',user='root',password='123456')
with db_conn.cursor() as cursor:
    cursor.execute(sql)
    db_conn.commit()
db_conn.close()
