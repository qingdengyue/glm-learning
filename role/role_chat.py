import streamlit as st


def read_lines_from_file(file_path):
    with open(file_path,'r',encoding="utf-8") as file:
       return [line.strip() for line in file.readlines()]


# 生成角色信息的函数（这里只是一个示例，你需要实现具体的逻辑）
def gen_role_data():
   # 这里应该是生成角色信息的逻辑
   st.session_state.role_name = "示例角色名称"
   st.session_state.role_gender = "男性"
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

def main():
   st.title('角色生成器')
 
   # 容器1和容器2并列
   col1, col2 = st.columns(2)
 
   with col1:
       st.subheader('容器1')
       # 输入框
       subject_info1 = st.text_input("输入主体信息")
       # 下拉框
       gender1 = st.selectbox("选择性别", ["男性", "女性", "未知"])

       # 下拉框
       personality1 = st.selectbox("选择性格", traits)
       mood_state1 = st.selectbox("选择心情", mood)
       psychological_state1 = st.selectbox("选择心理", pho)
       # 输入框
       role_description1 = st.text_input("生成的角色描述")
       # 只读输入框
       role_name1 = st.text_input("角色姓名", key="role_name1",disabled=True)
       role_gender1 = st.text_input("角色性别", key="role_gender1",disabled=True)
       role_personality1 = st.text_input("角色性格", key="role_personality1",disabled=True)
       role_mood1 = st.text_input("角色心情", key="role_mood1",disabled=True)
       role_psychological1 = st.text_input("角色心理", key="role_psychological1",disabled=True)
       # 图片框
       st.image("", width=100)  # 头像图片路径
       st.image("", width=300)  # 人设图片路径
 
   with col2:
       st.subheader('容器2')
       # 输入框
       subject_info2 = st.text_input("输入主体信息")
       # 下拉框
       gender2 = st.selectbox("选择性别", ["男性", "女性", "未知"])
       # 下拉框
       personality2 = st.selectbox("选择性格", traits)
       mood_state2 = st.selectbox("选择心情", mood)
       psychological_state2 = st.selectbox("选择心理", pho)
       # 输入框
       role_description2 = st.text_input("生成的角色描述")
       # 只读输入框
       role_name2 = st.text_input("角色姓名", key="role_name2",disabled=True)
       role_gender2 = st.text_input("角色性别", key="role_gender2",disabled=True)
       role_personality2 = st.text_input("角色性格", key="role_personality2",disabled=True)
       role_mood2 = st.text_input("角色心情", key="role_mood2",disabled=True)
       role_psychological2 = st.text_input("角色心理", key="role_psychological2",disabled=True)
       # 图片框
       st.image("", width=100)  # 头像图片路径
       st.image("", width=300)  # 人设图片路径
 
   # 容器3
   with st.container():
       st.subheader('容器3')
       # 按钮和点击事件
       if st.button("生成角色信息", key="gen_role"):
           gen_role_data()
       if st.button("生成对话信息", key="gen_message"):
           gen_message_data()


if __name__ == "__main__":
   main()