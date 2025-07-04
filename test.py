import time

from drug_parser import drug_parser
import pandas as pd
if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # df = pd.read_excel("./datas/数据.xlsx", header=0)
    # text = """
    # 药物英文名称，找出其对应的标准中文名称，上市情况，主要适应症，是否为复合配方，该成分常见商品名。按照表格输出。
    # 适应症需要按中国说明书和临床指南，列出的是在中国获批的、最重要的适应症（通常在说明书中列为“适应症”），不包括超说明书使用。适应症表述力求简洁清晰。
    # 每个药物解析后的结果以‘|’符号分隔，以下为你的回答格式参考示例(需严格遵守下面格式，返回的药物英文名称个数、顺序以及内容必须和查询列表中的药物英文名称一字不差):
    # 药物英文名称 | 标准中文名称 | 上市情况 | 主要适应症 | 复合配方 | 主要商品名
    # tacrolimus | 他克莫司 | 已上市 | 器官移植抗排斥 | 否 | 普乐可复/赛福开
    # fluticasone propionate;salmeterol | 氟替卡松/沙美特罗 | 已上市 | 哮喘/COPD | 是 | 舒利迭
    # venlafaxine | 文拉法辛 | 已上市 | 抑郁症 | 否 | 怡诺思/博乐欣
    # cupric chloride;manganese;potassium iodide;selenious acid;sodium fluoride;zinc chloride | 氯化铜;锰;碘化钾;亚硒酸;氟化钠;氯化锌 | 已上市 | 微量元素补充 | 是 | 无
    # 以下为需要对应的药物英文名称列表：
    # """
    # drug_parser(df, 3, "E:/workspace/drug_parse3", text)