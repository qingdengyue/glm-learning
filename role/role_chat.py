import requests
import time
import os
import random
import itertools
from typing import Literal, TypedDict, List, Union, Iterator, Optional

import jwt

import streamlit as st

class BaseMsg(TypedDict):
    pass



class TextMsg(BaseMsg):
    role: Literal["user", "assistant"]
    content: str


class CharacterMeta(TypedDict):
    role1_name:str
    role1_s:str
    role1_description:str
    role1_traits:str
    role1_mood:str
    role1_personality:str
    role1_icon:str
    role1_iamge_url:str
    role2_name:str
    role2_s:str
    role2_description:str
    role2_traits:str
    role2_mood:str
    role2_personality:str
    role2_icon:str
    role2_iamge_url:str

TextMsgList = List[TextMsg]


def read_lines_from_file(file_path):
    with open(file_path,'r',encoding="utf-8") as file:
       return [line.strip() for line in file.readlines()]


def gen_role1_description(meta:CharacterMeta):
    instructions=f"""
    你是一个优秀的电影编剧,非常擅长从人物的性格，心理，心情，简介中，生成一段人物设定描写。要求：
    1. 只生成人物设定描写信息,不包含人物姓名,不要生成多余内容。
    2. 不能包含敏感词,
    3. 不要超过300字

    简介:
    {meta["role1_description"]}

    性格:
    {meta["role1_traits"]}

    心情:
    {meta["role1_mood"]}

    心理:
    {meta["role1_personality"]}

    """
    return instructions


def gen_role_name(comments:str):
    instructions=f"""
    你是一个优秀的电影编剧,非常擅长从人物描述中为人物取名。要求：
    1. 名称可以为2个字,或者3个字。
    2. 结果只返回姓名,不需要包含其他内容

    人物描述:
    {comments}

    """
    return instructions




def gen_role2_description(meta:CharacterMeta):
    instructions=f"""
    你是一个优秀的电影编剧,非常擅长从人物的性格，心理，心情，简介中，生成一段人物设定描写。要求：
    1. 只生成人物设定描写信息,不包含人物姓名,不要生成多余内容。
    2. 不能包含敏感词,
    3. 不要超过300字

    简介:
    {meta["role2_description"]}

    性格:
    {meta["role2_traits"]}

    心情:
    {meta["role2_mood"]}

    心理:
    {meta["role2_personality"]}

    """
    return instructions


# 生成角色信息的函数（这里只是一个示例，你需要实现具体的逻辑）
def gen_role_data():
   # 这里应该是生成角色信息的逻辑
    """ 用chatglm生成人设设定信息 """
    
    instruction1 = gen_role1_description(st.session_state["meta"])
    role1_description= get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instruction1.strip()
            }
        ]
    )
    

    instruction1=gen_role_name(role1_description);
    role1_name= get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instruction1.strip()
            }
        ]
    )
    st.write(f"角色1姓名:{role1_name}")
    st.write(f"角色1设定:{role1_description}")
    

    instruction2 = gen_role2_description(st.session_state["meta"])
    role2_description= get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instruction2.strip()
            }
        ]
    )
   

    instruction2 = gen_role_name(role2_description)
    role2_name= get_chatglm_response_via_sdk(
        messages=[
            {
                "role": "user",
                "content": instruction2.strip()
            }
        ]
    )
    st.write(f"角色2姓名:{role2_name}")
    st.write(f"角色2设定:{role2_description}")
   # ... 更多的角色信息
 
# 生成对话信息的函数（这里只是一个示例，你需要实现具体的逻辑）
def gen_message_data():
   # 这里应该是生成对话信息的逻辑
   st.session_state.role_description = "这是一个生成的角色描述。"
   # ... 更多的对话信息


       # 从文件读取下拉框选项
traits = read_lines_from_file('traits.txt')
mood = read_lines_from_file('moods.txt')
pho = read_lines_from_file('psychological_traits.txt')

debug = os.getenv("DEBUG", "").lower() in ("1", "yes", "y", "true", "t", "on")

if "history" not in st.session_state:
    st.session_state.history = []

for history in st.session_state.history:
     with st.chat_message(history["role"]):
         st.markdown(history["content"])

if "meta" not in st.session_state:
    st.session_state.meta = {
       "role1_name":"角色1名称",
       "role1_s":"角色1性别",
       "role1_description":"角色1描述",
       "role1_traits":"角色1性格",
       "role1_mood":"角色1心情",
       "role1_personality":"角色1心理",
       "role1_icon":"角色1头像",
       "role1_iamge_url":"角色1人设图",
       "role2_name":"角色2名称",
       "role2_s":"角色2性别",
       "role2_description":"角色2描述",
       "role2_traits":"角色2性格",
       "role2_mood":"角色2心情",
       "role2_personality":"角色2性格",
       "role2_icon":"角色2头像",
       "role2_iamge_url":"角色2人设图",
    }






def generate_token(apikey: str, exp_seconds: int):
    # reference: https://open.bigmodel.cn/dev/api#nosdk
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)
 
    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
 
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


API_KEY: str = ""

def get_chatglm_response_via_sdk(messages: TextMsgList):
    """ 通过sdk调用chatglm """
    # reference: https://open.bigmodel.cn/dev/api#glm-3-turbo  `GLM-3-Turbo`相关内容
    # 需要安装新版zhipuai
    from zhipuai import ZhipuAI
    api_key=st.session_state["API_KEY"]
    print(f"apikey={api_key}")
    client = ZhipuAI(api_key=st.session_state["API_KEY"]) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=messages
    )
    print(f"response.choices[0].message.content")
    return response.choices[0].message.content


def update_api_key(key: Optional[str] = None):
    global API_KEY
    print(f'update_api_key. st.session_state["API_KEY"] = {st.session_state["API_KEY"]}, key = {key}')
    key = key or st.session_state["API_KEY"]
    if key:
        API_KEY = key

st.set_page_config(page_title="CharacterGLM Roles", page_icon="🤖", layout="wide")

def main():
   st.title('角色生成器')

   with st.container():
       st.text_input(label="API Key",value=os.getenv("API_KEY", ""), key="API_KEY", type="password", on_change=update_api_key)

 
   # 容器1和容器2并列
   col1, col2 = st.columns(2)
 
   with col1:
       st.subheader('角色1信息')
       # 输入框
       subject_info1 = st.text_input(label="角色1简介",key="role1_description", on_change=lambda : st.session_state["meta"].update(role1_description=st.session_state["role1_description"]))
       # 下拉框
       gender1 = st.selectbox(label="选择性别", options=["男性", "女性", "未知"],key="role1_s",on_change=lambda : st.session_state["meta"].update(role1_s=st.session_state["role1_s"]))

       # 下拉框
       personality1 = st.selectbox(label="选择性格",key="role1_traits",options= traits,on_change=lambda : st.session_state["meta"].update(role1_traits=st.session_state["role1_traits"]))
       mood_state1 = st.selectbox(label="选择心情",key="role1_mood", options=mood,on_change=lambda : st.session_state["meta"].update(role1_mood=st.session_state["role1_mood"]))
       psychological_state1 = st.selectbox(label="选择心理",key="role1_personality",options= pho,on_change=lambda : st.session_state["meta"].update(role1_personality=st.session_state["role1_personality"]))
       # 只读输入框
       role_name1 = st.text_input(label="角色1姓名", key="role1_name",disabled=True)
       global role_d1 
       role_d1= st.text_area(label="角色1设定信息", key="role1_d",disabled=True)
       # 图片框
       global role1_i1 
       role1_i1=st.image("default.jpg", width=100)  # 头像图片路径
       global role1_i2 
       role1_i2=st.image("default.jpg", width=300)  # 人设图片路径
 
   with col2:
       st.subheader('角色2信息')
        # 输入框
       subject_info2 = st.text_input(label="角色2简介",key="role2_description", on_change=lambda : st.session_state["meta"].update(role2_description=st.session_state["role2_description"]))
       # 下拉框
       gender2 = st.selectbox(label="选择性别", options=["男性", "女性", "未知"],key="role2_s",on_change=lambda : st.session_state["meta"].update(role2_s=st.session_state["role2_s"]))

       # 下拉框
       personality2 = st.selectbox(label="选择性格",key="role2_traits",options= traits,on_change=lambda : st.session_state["meta"].update(role2_traits=st.session_state["role2_traits"]))
       mood_state2 = st.selectbox(label="选择心情",key="role2_mood", options=mood,on_change=lambda : st.session_state["meta"].update(role2_mood=st.session_state["role2_mood"]))
       psychological_state2 = st.selectbox(label="选择心理",key="role2_personality",options= pho,on_change=lambda : st.session_state["meta"].update(role2_personality=st.session_state["role2_personality"]))
       # 只读输入框
       role_name2 = st.text_input(label="角色2姓名", key="role2_name",disabled=True)
       global role_d2
       role_d2 = st.text_area(label="角色2设定信息", key="role2_d",disabled=True)
       # 图片框
       global role2_i1
       role2_i1=st.image("default.jpg", width=100)  # 头像图片路径
       global role2_i2
       role2_i2=st.image("default.jpg", width=300)  # 人设图片路径
 
   # 容器3
   with st.container():
       st.subheader('角色信息生成')
       # 按钮和点击事件
       if st.button(label="生成角色信息", key="gen_role"):
           gen_role_data()
       if st.button(label="生成对话信息", key="gen_message"):
           gen_message_data()

   with st.container():
       st.subheader('对话生成区域')
       query=st.chat_input("等待对话生成")
       if not query:
           return
        

if __name__ == "__main__":
   main()