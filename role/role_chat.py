import requests
import time
import os
import random
import itertools
from typing import Literal, TypedDict, List, Union, Iterator, Optional

import jwt

import streamlit as st
st.set_page_config(page_title="CharacterGLM Roles", page_icon="🤖", layout="wide")
class BaseMsg(TypedDict):
    pass



class TextMsg(BaseMsg):
    role: Literal["user", "assistant"]
    content: str


class CharacterMeta(TypedDict):
    role1_name:str
    role1_s:str
    role1_description:str
    role1_d:str
    role1_traits:str
    role1_mood:str
    role1_personality:str
    role1_icon:str
    role1_iamge_url:str
    role2_name:str
    role2_s:str
    role2_description:str
    role2_d:str
    role2_traits:str
    role2_mood:str
    role2_personality:str
    role2_icon:str
    role2_iamge_url:str

TextMsgList = List[TextMsg]
MsgList = List[TextMsg]

def read_lines_from_file(file_path):
    with open(file_path,'r',encoding="utf-8") as file:
       return [line.strip() for line in file.readlines()]


def gen_role1_description(meta:CharacterMeta):
    instructions=f"""
    你是一个优秀的电影编剧,非常擅长从人物的性格，心理，心情，简介中，生成一段人物设定描写。要求：
    1. 只生成人物设定描写信息,不包含人物姓名,不要生成多余内容。
    2. 不能包含敏感词.
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


def filter_text_msg(messages: MsgList) -> TextMsgList:
    return [m for m in messages if m["role"] != "image"]


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
    st.session_state["meta"]["role1_name"]=role1_name
    st.session_state["meta"]["role1_d"]=role1_description

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
    st.session_state["meta"]["role2_name"]=role2_name
    st.session_state["meta"]["role2_d"]=role2_description

    st.write(f"角色1头像:")
    role1_icon=get_cogview_response(role1_description)
    print(f"角色1头像:{role1_icon}")
    st.image(role1_icon, width=100)

    st.write(f"角色2头像:")
    role2_icon=get_cogview_response(role2_description)
    print(f"角色2头像:{role2_icon}")
    st.image(role2_icon, width=100)

    st.write(f"角色1人设图:")
    role1_iamge_url=get_cogview_response_design(role1_description)
    print(f"角色1人设图:{role1_iamge_url}")
    st.image(role1_iamge_url, width=720)


    st.write(f"角色2人设图:")
    role2_iamge_url=get_cogview_response_design(role2_description)
    st.image(role2_iamge_url, width=720)

    st.write(f"生成2个角色的10条对话信息:")

    
    #每次为新对话
    st.session_state.history = [] 
    query="今日所谓何事?"
    st.session_state["history"].append(TextMsg({"role": "user", "content": query}))
    print(f"role:user,response:{query}")
    for i in range(10):
        role='assistant' if i%2==0 else 'user'
        response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=get_meta_characterglm_response(st.session_state["meta"]))
        bot_response = output_stream_response(response_stream)
        if not bot_response:
            st.session_state["history"].pop()
        else:
            print(f"role:{role},response:{bot_response}")
            st.session_state["history"].append(TextMsg({"role": role, "content": bot_response}))
           

    print(f"st.session_state.history = {st.session_state.history}")
    for history in st.session_state.history:
        with st.chat_message(name=history["role"], avatar=role1_icon if history["role"] == "user" else role2_icon):
            st.markdown(history["content"])
    text_content=[];
    for history in st.session_state.history:
       if history["role"] == "user":
           text_content.append(f"{role1_name}:{history['content']}")
       else:
           text_content.append(f"{role2_name}:{history['content']}")

    file_content="\n".join(text_content)
    st.download_button(
        label="对话下载:",
        data=file_content,
        file_name="chatglm_roles.txt",
    )
   # ... 更多的角色信息


       # 从文件读取下拉框选项
traits = read_lines_from_file('traits.txt')
mood = read_lines_from_file('moods.txt')
pho = read_lines_from_file('psychological_traits.txt')

debug = os.getenv("DEBUG", "").lower() in ("1", "yes", "y", "true", "t", "on")

if "history" not in st.session_state:
    st.session_state.history = []

# for history in st.session_state.history:
#      with st.chat_message(history["role"]):
#          st.markdown(history["content"])

if "meta" not in st.session_state:
    st.session_state.meta = {
       "role1_name":"角色1名称",
       "role1_s":"角色1性别",
       "role1_description":"角色1描述",
       "role1_d":"角色1描述",
       "role1_traits":"角色1性格",
       "role1_mood":"角色1心情",
       "role1_personality":"角色1心理",
       "role1_icon":"角色1头像",
       "role1_iamge_url":"角色1人设图",
       "role2_name":"角色2名称",
       "role2_s":"角色2性别",
       "role2_description":"角色2描述",
       "role2_d":"角色2描述",
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


def get_cogview_response(query: str):
    prompt=f"""
    100x100像素，高清，中国古风，长发飘逸，剑眉星目，白衣如雪，背景为淡淡的云雾，水墨渲染，具有中国古代绘画风格。
    {query}
    """
    from zhipuai import ZhipuAI
    api_key=st.session_state["API_KEY"]
    print(f"apikey={api_key}")
    client = ZhipuAI(api_key=st.session_state["API_KEY"]) # 请填写您自己的APIKey
    response = client.images.generations(
    model="cogview-3", #填写需要调用的模型名称
    prompt=prompt,
    )
    image_url=response.data[0].url
    print(f"图片已生成:{image_url}")
    return image_url

def get_cogview_response_design(query: str):
    prompt=f"""
    请生成一张720x1280像素的人物设计图，展现一位仙侠风格的英雄形象。图中角色应穿着传统古装，手持武器，背景为神秘的山林或云海，色彩淡雅，具有中国水墨画风。角色动作生动，表情专注，适合16:9宽屏手机端查看。
    {query}
    """
    from zhipuai import ZhipuAI
    api_key=st.session_state["API_KEY"]
    print(f"apikey={api_key}")
    client = ZhipuAI(api_key=st.session_state["API_KEY"]) # 请填写您自己的APIKey
    response = client.images.generations(
    model="cogview-3", #填写需要调用的模型名称
    prompt=prompt,
    )
    image_url=response.data[0].url
    print(f"图片已生成:{image_url}")
    return image_url


def get_meta_characterglm_response(meta:CharacterMeta):
   return {
       "user_info":meta["role1_d"],
       "user_name":meta["role1_name"],
       "bot_info":meta["role2_d"],
       "bot_name":meta["role2_name"],
   }




def get_characterglm_response(messages: TextMsgList, meta):
    """ 通过http调用characterglm """
    # Reference: https://open.bigmodel.cn/dev/api#characterglm
    api_key=st.session_state["API_KEY"]
    url = "https://open.bigmodel.cn/api/paas/v3/model-api/charglm-3/sse-invoke"
    resp = requests.post(
        url,
        headers={"Authorization": generate_token(api_key, 1800)},
        json=dict(
            model="charglm-3",
            meta=meta,
            prompt=messages,
            incremental=True)
    )
    resp.raise_for_status()
    
    # 解析响应（非官方实现）
    sep = b':'
    last_event = None
    for line in resp.iter_lines():
        if not line or line.startswith(sep):
            continue
        field, value = line.split(sep, maxsplit=1)
        if field == b'event':
            last_event = value
        elif field == b'data' and last_event == b'add':
            yield value.decode()


def output_stream_response(response_stream: Iterator[str]):
    stream_value=[]
    for content in itertools.accumulate(response_stream):
        stream_value.append(content)
    return "".join(stream_value)



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
 
   # 容器3
   with st.container():
       st.subheader('角色信息生成')
       # 按钮和点击事件
       if st.button(label="生成角色信息", key="gen_role"):
           gen_role_data()
        

if __name__ == "__main__":
   main()