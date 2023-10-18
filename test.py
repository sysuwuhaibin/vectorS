import streamlit as st
from milvus_utility import MilvusUtility
from openai_utility import ChatBot
import openai
import numpy as np
import configparser
import logging


# 创建日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建日志格式器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)

# 创建一个ConfigParser对象
config = configparser.ConfigParser()

# 创建一个ConfigParser对象
config = configparser.ConfigParser()

# 读取INI文件
config.read('setting.ini', encoding='utf-8')

# 预处理提示的函数
def preprocess_prompt(promt_embedding_res, text, namespace):
    try:
        prompt_final = {
            "system": '',
            "user": ''
        }
        if config.get('Model', 'selected_model') == 'Pinecone':
            prompt_res = PineconeUtility().query_pinecone(promt_embedding_res, namespace)
            logger.info("从Pinecone知识库中检索相关内容：完成")
            # 重新构造提示
            contexts1 = ["\n【相关度】" + str(item['score']) + "\n【候选结果" + str(i + 1) + "】\n" + item['metadata'][
                'data'].lstrip('') for
                         i, item in enumerate(prompt_res['matches'])]
            contexts = [item['metadata']['data'] for item in prompt_res['matches']]
            result = "\n【查询问题】 " + text + "\n===================================================" + \
                     "\n===================================================".join(contexts1) + "\n"
            prompt_final['system'] = ''.join(contexts)
            prompt_final['user'] = text
            logger.info("重新构造提示：完成")
        elif config.get('Model', 'selected_model') == 'Milvus':
            Milvus_TOP_K = config.getint('Milvus', 'top_k')
            prompt_res = MilvusUtility().search_entity("GUIHUAZHIXUN", promt_embedding_res)
            print(prompt_res)
            logger.info("从Milvus知识库中检索相关内容：完成")
            # 重新构造提示
            contexts1 = [" 候选结果" + str(i + 1) + "   相关度:" + str(1 - item.distance) + " =======================\n" + \
                         '【问题分类】' + item.entity.get('classification') + '\n【问题标题】' + item.entity.get(
                'description') + '\n【问题描述】' + item.entity.get('content') for i, item in enumerate(prompt_res[0])]
            contexts = ['\n【问题分类】' + item.entity.get('classification') + '\n【问题标题】' + item.entity.get(
                'description') + '\n【问题描述】' + item.entity.get('content') for item in prompt_res[0]]
            result = "\n【查询问题】 " + text + "\n=======================" + \
                     "\n=======================".join(contexts1) + "\n\n"
            prompt_final['system'] = ' '.join(contexts)
            prompt_final['user'] = text
            logger.info("重新构造提示：完成")
        return prompt_final, result

    except Exception as e:
        logger.error("预处理提示时出现异常:", str(e))
        return None, None

openai.api_base = "http://ai.hellopas.com:3000/v1"
openai.api_key = "sk-2bH7CNR4jC3ZL00MF6BfFf5848A74c64A09c4d4eFeAf2d65"

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


prompt = st.chat_input("请输入")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

def chat(text):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': text}
        ],
        temperature=0
    )

    return response.choices[0].message.content

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            embedding_res = ChatBot().generate_embedding(prompt)
            prompt_final, result = preprocess_prompt(embedding_res, prompt, namespace="dddd")
            print(prompt_final)
            completion = ChatBot().interact_with_llm(prompt_final)
            response = prompt_final['system'] + completion
            placeholder = st.empty()
            full_response = response
            placeholder.text(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
