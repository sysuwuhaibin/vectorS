import streamlit as st
import openai
import numpy as np

openai.api_base = "http://ai.hellopas.com:3000/v1"
openai.api_key = "sk-2bH7CNR4jC3ZL00MF6BfFf5848A74c64A09c4d4eFeAf2d65"

with st.chat_message("user"):
    st.write("Hello 👋")
    st.write("Nice 👋")

message = st.chat_message("assistant")
message.write("Hello human")

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)

response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': '你吃饭了吗'}
    ],
    temperature=0,
    stream=True
)

collected_chunks = []
collected_messages = []
# iterate through the stream of events
for chunk in response:
    chunk_time = time.time() - start_time  # calculate the time delay of the chunk
    collected_chunks.append(chunk) 
    chunk_message = chunk['choices'][0]['delta']  # extract the message
    collected_messages.append(chunk_message)  # save the message
    message = st.chat_message("assistant")
    message.write(collected_messages)
