import configparser
import datetime
import logging
import pinecone


class PineconeUtility:
    def __init__(self, config_file='setting.ini', log_file='app.log'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

        # 获取Database部分的配置信息
        self.PINECONE_API_KEY = self.config.get('Pinecone', 'api_key')
        self.PINECONE_ENVIRONMENT = self.config.get('Pinecone', 'environment')
        self.PINECONE_TOP_K = self.config.getint('Pinecone', 'top_k')

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

        # 初始化 OpenAI 和 Pinecone
        pinecone.init(api_key=self.PINECONE_API_KEY, environment=self.PINECONE_ENVIRONMENT)

        # 初始化索引
        active_indexes = pinecone.list_indexes()
        self.index1 = pinecone.Index(active_indexes[0])

    # 查询 Pinecone 的函数
    def query_pinecone(self, content, namespace):
        try:
            print(self.PINECONE_TOP_K)
            prompt_res = self.index1.query(content, top_k=self.PINECONE_TOP_K, include_metadata=True,
                                           namespace=namespace)
            return prompt_res
        except Exception as e:
            self.logger.error("查询Pinecone索引时出现异常:", e)

    # 更新 Pinecone 索引的函数
    def update_pinecone_index(self, data_embedding_res, content, namespace):
        try:
            # 使用新数据更新 Pinecone 索引
            self.index1.upsert([("q" + str(datetime.datetime.now()), data_embedding_res, {"data": content})],
                               namespace=namespace)
            self.logger.info("更新知识库向量及其元数据：完成")
        except Exception as e:
            self.logger.error("更新Pinecone索引时出现异常:", str(e))
