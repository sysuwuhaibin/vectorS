import configparser
import logging
from pymilvus import (
    connections,
    db,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)


class MilvusUtility:
    def __init__(self, config_file='setting.ini', log_file='app.log'):
        # 创建一个ConfigParser对象
        self.config = configparser.ConfigParser()
        # 读取INI文件
        self.config.read(config_file, encoding='utf-8')

        # 获取Database部分的配置信息
        self.milvus_host = self.config.get('Milvus', 'host')
        self.milvus_port = self.config.getint('Milvus', 'port')

        # 创建日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建日志格式器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将文件处理器添加到日志记录器
        self.logger.addHandler(file_handler)

        self.top_k = self.config.getint('Milvus', 'top_k')

        # 使用默认数据库 ‘default’,也可以自己建数据库
        try:
            connections.connect('default', host=self.milvus_host, port=self.milvus_port)
            db.using_database("default")
        except Exception as e:
            self.logger.error(f"Milvus连接错误: {str(e)}")

    def create_collection(self, collection_name):
        try:
            dim = 1536
            fields = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                      FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535, description="content"),
                      FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim),
                      ]
            schema = CollectionSchema(fields, description='desc of collection')
            collection = Collection(name=collection_name, schema=schema, consistency_level="Strong")
            index = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128},
            }
            collection.create_index("embeddings", index)
            return collection
        except Exception as e:
            self.logger.error(f"创建collection错误: {str(e)}")
            return None

    def create_collection1(self, collection_name):
        try:
            dim = 1536
            fields = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                      FieldSchema(name="classification", dtype=DataType.VARCHAR, max_length=65535, description="classification"),
                      FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=65535, description="description"),
                      FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535, description="content"),
                      FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim),
                      ]
            schema = CollectionSchema(fields, description='desc of collection')
            collection = Collection(name=collection_name, schema=schema, consistency_level="Strong")
            index = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128},
            }
            collection.create_index("embeddings", index)
            return collection
        except Exception as e:
            self.logger.error(f"创建collection错误: {str(e)}")
            return None

    def insert_entity(self, collection_name, entity_list):
        try:
            collection = Collection(name=collection_name)
            collection.load()
            collection.insert(entity_list)
            collection.flush()
            self.logger.info("插入实体：完成")
        except Exception as e:
            self.logger.error("插入实体时出现异常:", str(e))

    def search_entity(self, collection_name, query_embedding):
        try:
            collection = Collection(name=collection_name)
            collection.load()
            search_vectors = [query_embedding]
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            res = collection.search(
                search_vectors,
                "embeddings",
                search_params,
                limit=self.top_k,
                output_fields=["classification", "description", "content", 'note', 'translate']
            )
            self.logger.info("查询结果：完成")
            return res
        except Exception as e:
            self.logger.error("查询实体时出现异常:", str(e))
            return None

    def get_entity_list(self, collection_name):
        try:
            collection = Collection(name=collection_name)
            collection.load()
            res = collection.get_entity_list()
            self.logger.info("获取实体列表：完成")
            return res
        except Exception as e:
            self.logger.error("获取实体列表时出现异常:", str(e))
            return None

    def delete_entity(self, collection_name, entity_id):
        try:
            collection = Collection(name=collection_name)
            collection.load()
            collection.delete(entity_id)
            self.logger.info("删除实体：完成")
        except Exception as e:
            self.logger.error("删除实体时出现异常:", str(e))

    def delete_collection(self, collection_name):
        try:
            collection = Collection(name=collection_name)
            collection.load()
            collection.drop()
            self.logger.info("删除集合：完成")
        except Exception as e:
            self.logger.error("删除集合时出现异常:", str(e))
