import time
import streamlit as st
from drug_parser import drug_parser
import pandas as pd

st.title("🦜🔗 药物解析工具")
with st.sidebar:
    uploaded_file = st.file_uploader("上传数据文件", type=("xlsx", "csv"), help="拖放文件到这里或浏览本地文件")
    threads = st.slider(label='请选择进程数', min_value=1, max_value=16, value=1, step=1, help="根据进程数")
    output_dir = st.text_input("输出文件目录", value="./output")

with st.form("my_form"):
    text = st.text_area("请输入提示词:", """
    药物英文名称，找出其对应的标准中文名称，上市情况，主要适应症，是否为复合配方，该成分常见商品名。按照表格输出。
    适应症需要按中国说明书和临床指南，列出的是在中国approved的、最重要的适应症（通常在说明书中列为“适应症”），不包括超说明书使用。适应症表述力求简洁清晰。
    每个药物解析后的结果以‘|’符号分隔，以下为你的回答格式参考示例(需严格遵守下面格式，药物英文名称保持原有单词，不要拆分，比如‘adenine;citric acid;d-glucose;sodium chloride;sodium citrate;sodium phosphate’，解析后药物英文名称还是这个):
    药物英文名称 | 标准中文名称 | 上市情况 | 主要适应症 | 复合配方 | 主要商品名
    tacrolimus | 他克莫司 | 已上市 | 器官移植抗排斥 | 否 | 普乐可复/赛福开
    fluticasone propionate;salmeterol | 氟替卡松/沙美特罗 | 已上市 | 哮喘/COPD | 是 | 舒利迭
    venlafaxine | 文拉法辛 | 已上市 | 抑郁症 | 否 | 怡诺思/博乐欣
    cupric chloride;manganese;potassium iodide;selenious acid;sodium fluoride;zinc chloride | 氯化铜;锰;碘化钾;亚硒酸;氟化钠;氯化锌 | 已上市 | 微量元素补充 | 是 | 无
    以下为需要对应的药物英文名称列表：
 """, height=300)
    submitted = st.form_submit_button("提交")
    if not uploaded_file:
        st.warning("请先上传数据文件！")
    elif submitted:
        st.info(f"解析中... 时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            with st.spinner("药物解析中，请稍候..."):
                drug_parser(df, threads, output_dir, text)
                st.success(f'已完成! 时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        except Exception as e:
            st.error(f'报错:{str(e)}! 时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
