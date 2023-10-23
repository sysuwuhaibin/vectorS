import streamlit as st
from milvus_utility import MilvusUtility
from openai_utility import ChatBot
import openai
import numpy as np
import os
import configparser
import logging

st.set_page_config(page_title="💬 Tiancom VectorS",layout="wide")

with st.sidebar:
    st.title('💬 Tiancom VectorS')
    if 'OPENAI_BASE_URL' in st.secrets:
        text = 'OPENAI_BASE_URL\n' + st.secrets['OPENAI_BASE_URL']
        st.success(text, icon='✅')
        openai_base_url = st.secrets['OPENAI_BASE_URL']
    else:
        openai_base_url = st.text_input('请输入OPENAI BASE URL:', type='default')
        if not (openai_base_url.startswith('http') and len(openai_base_url) > 10):
            st.warning('请输入正确的OPENAI BASE URL！', icon='⚠️')
        else:
            st.success('OPENAI BASE URL已输入！', icon='✅')
    os.environ['OPENAI_BASE_URL'] = openai_base_url
    if 'OPENAI_API_TOKEN' in st.secrets:
        st.success('API key已经提供!', icon='✅')
        openai_api = st.secrets['OPENAI_API_TOKEN']
    else:
        openai_api = st.text_input('请输入OPENAI API KEY:', type='password')
        if not (openai_api.startswith('sk-') and len(openai_api)==51):
            st.warning('请输入正确的OPENAI API KEY！', icon='⚠️')
        else:
            st.success('OPENAI API key已输入', icon='✅')
    os.environ['OPENAI_API_TOKEN'] = openai_api

    #st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')
    recommend_degree = st.slider('推荐程度设置：', 0.0, 1.0, 0.75)

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "您好，我是你的规划咨询小助手VectorS，请告诉我，你们存在的问题。我将会为你指出问题的类型及其建议哦！"}]
st.sidebar.button('清除聊天历史', on_click=clear_chat_history)

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
            prompt_res = MilvusUtility().search_entity("GUIHUAZHIXUN", promt_embedding_res, ["classification", "description", "content"])
            print(prompt_res)
            logger.info("从Milvus知识库中检索相关内容：完成")
            # 重新构造提示
            contexts1 = [" 候选结果" + str(i + 1) + "   相关度:" + str(1 - item.distance) + " =======================\n" + \
                         '【问题分类】' + item.entity.get('classification') + '\n【问题标题】' + item.entity.get(
                'description') + '\n【问题描述】' + item.entity.get('content') for i, item in enumerate(prompt_res[0])]
            contexts = ["对不起，知识库中没有符合您的问题的建议！"]
            if float(1 - prompt_res[0][0].distance) > recommend_degree:
                contexts = ['\n【推荐程度】' + str(1 - item.distance) + '\n\n【问题分类】' + item.entity.get('classification') + '\n\n【问题标题】' + item.entity.get(
                    'description') + '\n\n【问题描述】' + item.entity.get('content') for item in prompt_res[0]]
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
    st.session_state.messages = [{"role": "assistant", "content": "您好，我是你的规划咨询小助手VectorS，请告诉我，你们存在的问题。我将会为你指出问题的类型及其建议哦！"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


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
        with st.spinner("正在思考中..."):
            embedding_res = ChatBot().generate_embedding(prompt)
            prompt_final, result = preprocess_prompt(embedding_res, prompt, namespace="dddd")
            if prompt_final is not None and prompt_final['system'] != '对不起，知识库中没有符合您的问题的建议！':
                completion = ChatBot().interact_with_llm(prompt_final)
                response = prompt_final['system'] + '\n\n' + completion
            elif prompt_final is None:
                response = '当前服务不可用，很抱歉！'
            else:
                response = '对不起，知识库中没有符合您的问题的建议！'
            placeholder = st.empty()
            full_response = response
            placeholder.markdown(full_response, unsafe_allow_html=True)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
    st.balloons()
