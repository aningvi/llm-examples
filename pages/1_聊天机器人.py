from openai import OpenAI
import streamlit as st

with st.sidebar:
    openai_api_key = st.text_input("DeepSeek API Key", key="chatbot_api_key", type="password")

st.title("💬 药物解析DeepSeek-V3")
st.caption("🚀 药物解析系统")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "你是一名专业的医药专家"},{"role": "user", "content": "请输入提示词"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("请输入DeepSeek API key 继续使用.")
        st.stop()

    client = OpenAI(api_key=openai_api_key, base_url='https://api.lkeap.cloud.tencent.com/v1')
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="deepseek-v3", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "system", "content": msg})
    st.chat_message("system").write(msg)
