# import xlrd
# from milvus_utility import MilvusUtility
# from openai_utility import ChatBot
#
# MilvusUtility().create_collection1('GUIHUAZHIXUN')
# # 打开Excel文件
# workbook = xlrd.open_workbook('E:\项目管理\FastGPT问答\规划咨询问题集.xls')
#
# # 获取第一个工作表
# worksheet = workbook.sheet_by_index(0)
#
# i = 1
# # 遍历行
# for row in range(worksheet.nrows):
#     # 遍历列
#     cell_value = worksheet.cell_value(row, 2)
#     print(cell_value)
#     data_embedding_res0 = ChatBot().generate_embedding(str(cell_value))
#     MilvusUtility().insert_entity('GUIHUAZHIXUN', [
#         {'classification': worksheet.cell_value(row, 0), 'description': worksheet.cell_value(row, 1),
#          'content': worksheet.cell_value(row, 2),
#          'embeddings': data_embedding_res0}])
#     print(i)
#     i += 1
import streamlit as st
import pandas as pd

st.write("""
# My first app
## dffdf
Hello *world!*

- ddfdf
- dfdfd
- dfsfd
""")

df = pd.read_excel("E:\\项目管理\\FastGPT问答\\23.xls")
st.altair_chart(df)

st.table(df)

