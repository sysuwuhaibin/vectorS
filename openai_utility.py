import configparser
import logging
import openai


class ChatBot:
    def __init__(self):
        # 创建日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 创建文件处理器
        file_handler = logging.FileHandler('app.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建日志格式器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将文件处理器添加到日志记录器
        self.logger.addHandler(file_handler)

        # 创建一个ConfigParser对象
        self.config = configparser.ConfigParser()

        # 读取INI文件
        self.config.read('setting.ini', encoding='utf-8')

        # 获取Database部分的配置信息
        openai.api_base = os.environ['OPENAI_BASE_URL']
        openai.api_key = os.environ['OPENAI_API_TOKEN']

    def generate_embedding(self, text):
        try:
            # 使用 OpenAI API 生成嵌入向量
            promt_embedding_res = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=text
            )
            self.logger.info("生成问题embedding向量：完成")
            return promt_embedding_res['data'][0]['embedding']
        except Exception as e:
            self.logger.error("生成嵌入向量时出现异常:", str(e))
            return None

    def interact_with_llm(self, prompt_final):
        try:
            # 使用 OpenAI API 与 LLM 交互
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": '```背景知识：' + prompt_final['system'] + '```\n\n请你根据背景知识回答我的问题，回答的内容使用markdown语法输出，最好能格式化，分点有条理的输出。如果背景知识无法回答该问题，请回复“我不知道”。'},
                    {"role": "user", "content": '”我的问题：' + prompt_final['user']},
                ]
            )
            self.logger.info("LLM回答：完成")
            return completion.choices[0].message.content.replace('\n\n', '\n')
        except Exception as e:
            self.logger.error("与LLM交互时出现异常:", str(e))
            return None
