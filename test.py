import streamlit as st
import numpy as np

with st.chat_message("user"):
    st.write("Hello 👋")
    st.write("Nice 👋")

message = st.chat_message("assistant")
message.write("Hello human")
