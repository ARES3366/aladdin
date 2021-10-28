import os
import unittest
from init.utils import get_mongo_client, read_config_infile, mongo_config
from urllib.parse import quote_plus


class TestExtractMethod(unittest.TestCase):
    def test_read_config_file(self):
        mongo_conf = read_config_infile("mongodb", "/root/server_test.conf")
        self.assertFalse(mongo_conf)

        mongo_conf["host"] = "aladdin-cas"
        self.assertTrue(mongo_conf)

    def test_get_mongo_client(self):
        mongodb_conf = read_config_infile("mongodb", "/root/server_test.conf")
        mongo_config = dict(
            host=mongodb_conf.get('host', "aladdin-cas-mongo").replace('"', ''),
            port=int(mongodb_conf.get('port', "27017").replace('"', '')),
            db_auth=mongodb_conf.get("db_auth", "admin").replace('"', ''),
            db=mongodb_conf.get("db", "aladdin-cas").replace('"', ''),
            user=quote_plus(mongodb_conf.get("user", "").replace('"', '')),
            password=quote_plus(mongodb_conf.get("password", "").replace('"', '')),
            replicaSet=quote_plus(mongodb_conf.get("replicaSet", "").replace('"', '')),
            sslCAFile=quote_plus(mongodb_conf.get("sslCAFile", "").replace('"', '')),
            ssl=quote_plus(mongodb_conf.get("ssl", "").replace('"', '')),
            options=mongodb_conf.get("options", str(dict())).strip(),
        )
        _, uri = get_mongo_client(mongo_config)
        self.assertEqual(uri, "mongodb://aladdin-cas-mongo:27017/admin")

        mongo_config["options"] = 'authSource: ""'
        _, uri = get_mongo_client(mongo_config)
        self.assertEqual(uri, "mongodb://aladdin-cas-mongo:27017/admin")

        mongo_config["options"] = 'authSource: "null"'
        _, uri = get_mongo_client(mongo_config)
        self.assertEqual(uri, "mongodb://aladdin-cas-mongo:27017/admin")

        mongo_config["options"] = 'authSource: "True"'
        _, uri = get_mongo_client(mongo_config)
        self.assertEqual(uri, "mongodb://aladdin-cas-mongo:27017/admin&authSource=True")


if __name__ == "__main__":
    unittest.main()