# -- coding: utf-8 --**
import glob
import os
import pandas as pd
from openai import OpenAI
import time
import multiprocessing
import logging
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(process)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=f"drug_parser.log",
    filemode='a'

)


def get_processed_drugs(drugs_table):
    file_path = drugs_table + '.txt'
    drug_list = []
    if os.path.exists(file_path):
        # 读取file_path文件中的第一列存入数组
        with open(file_path, 'r', encoding='gbk') as f:
            lines = f.readlines()
            for line in lines:
                drug_list.append(line.strip().split('|')[0].strip())
    return drug_list

def save_processed_errors(error, drugs, result, error_reson, errors_table):
    # 检查文件是否存在，决定是否写入表头
    file_path = f"{errors_table}.txt"
    with open(file_path, 'a', encoding='gbk') as f:
        f.write(error + '\t')
        f.write(drugs + '\t')
        f.write(result + '\t')
        f.write(error_reson + '\n')


def save_processed_drugs(results, drugs_table):
    process_name = os.path.basename(drugs_table)
    """批量保存处理结果到txt文件，支持动态表名"""
    file_path = f"{drugs_table}.txt"
    # 写入txt文件
    with open(file_path, 'a', encoding='gbk') as f:
        for result in results:
            f.write(result + '\n')
    logging.info(f"进程【{process_name}】成功保存 {len(results)} 条药物记录到 {file_path}")


def standardize_drug_names_batch(drug_names, drugs_table, errors_table, batch_size, system_prompt):
    # 获取文件地址的文件名
    process_name = os.path.basename(drugs_table)
    # 配置API参数
    client = OpenAI(
        api_key=config['api']['api_key'],
        base_url=config['api']['base_url'],
    )
    """批量调用DeepSeek-V3 API进行标准化处理，支持动态表名"""
    for i in range(0, len(drug_names), batch_size):
        result = ""
        batch = drug_names[i:i + batch_size]
        batch_str = "\n".join(batch)
        logging.info(
            f"进程【{process_name}】构建response。解析{len(batch)}个药物：{batch[0]} - {batch[len(batch) - 1]}")
        try:
            print(f"进程【{process_name}】构建response。解析{batch[0]} - {batch[len(batch) - 1]}")
            response = client.chat.completions.create(
                model="deepseek-v3",
                messages=[
                    {"role": "system", "content": "你是一名专业的医药专家,最后仅输出对应表即可，不要其他多余的内容。"},
                    {"role": "user", "content": f"{system_prompt}\n{batch_str}"},
                ],
                temperature=float(config['api']['temperature']),
                max_tokens=int(config['api']['max_tokens'])
            )
            logging.info(f"进程【{process_name}】开始调用接口。")
            result = response.choices[0].message.content
            logging.info(f"进程【{process_name}】API已返回内容，返回内容长度：{len(result)}。开始解析。")
            if not result or not isinstance(result, str) or len(result.strip()) == 0:
                logging.error(f"进程【{process_name}】API返回内容为空或格式异常，跳过本批次。")
                save_processed_errors("API返回内容为空或格式异常", f"错误行：{i} - {i + batch_size - 1}", result,
                                      "返回内容为空或格式异常", errors_table)
                continue
            try:
                save_processed_drugs(
                    result.strip().split('\n'),
                    drugs_table)
            except Exception as e:
                logging.error(
                    f"进程【{process_name}】解析表格格式失败: {str(e)}\n原始API返回内容: {result}")
                save_processed_errors("解析表格格式失败", f"错误行：{i} - {i + batch_size - 1}", result, str(e),
                                      errors_table)

        except Exception as e:
            logging.error(f"进程【{process_name}】请求参数：" + batch_str)
            logging.error(f"进程【{process_name}】API调用失败: {str(e)}")
            save_processed_errors("API调用失败", f"错误行：{i} - {i + batch_size - 1}", result, str(e), errors_table)
        finally:
            time.sleep(3)


def process_drug_chunk(drug_names, drugs_table, errors_table, system_prompt):
    process_name = os.path.basename(drugs_table).split('_')[2]
    logging.info(f"进程【{process_name}】启动: {drugs_table}，进程分配数据量: {len(drug_names)}")
    processed_drugs = get_processed_drugs(drugs_table)
    logging.info(f"进程【{process_name}】已处理 {len(processed_drugs)} 条数据")
    unprocessed_names = [name for name in drug_names if name not in processed_drugs]

    if unprocessed_names:
        logging.info(f"进程【{process_name}】实际处理数据量： {len(unprocessed_names)}")
        standardize_drug_names_batch(unprocessed_names, drugs_table, errors_table,
                                     batch_size=int(config['process']['batch_size']), system_prompt=system_prompt)
    logging.info(f"进程【{process_name}】处理完成！")


def main(df, num_workers, output_path, system_prompt):
    start_index = int(config['process']['start_index'])
    max_record = int(config['process']['max_record'])
    # 按中文编码读取
    raw_names = df.iloc[:, 1].tolist()
    raw_names = [name for name in raw_names if pd.notna(name)]
    raw_names = [name.strip() for name in raw_names]
    raw_names = list(dict.fromkeys(raw_names))
    total = len(raw_names)
    end_index = total if max_record == -1 else start_index + max_record
    raw_names = raw_names[start_index: end_index]
    logging.info(f"本批次解析数据：{start_index} ~ {end_index - 1}")
    logging.info(f"原始数据行数: {total}")

    if num_workers == 1:
        # 单进程模式
        logging.info("使用单进程模式处理数据")
        drugs_table = os.path.join(output_path, "processed_drugs_single")
        errors_table = os.path.join(output_path, "processed_errors_single")
        process_drug_chunk(raw_names, drugs_table, errors_table, system_prompt)
    else:
        # 多进程模式
        chunk_size = total // num_workers
        processes = []
        for i in range(num_workers):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < num_workers - 1 else total
            chunk = raw_names[start:end]
            drugs_table = os.path.join(output_path, f"processed_drugs_worker{i + 1}")
            errors_table = os.path.join(output_path, f"processed_errors_worker{i + 1}")
            p = multiprocessing.Process(target=process_drug_chunk, args=(chunk, drugs_table, errors_table, system_prompt))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

    logging.info("全部进程处理完成！")

def merge_all_data(output_path):
    result_file_path = os.path.join(output_path, 'results.txt')
    all_files = glob.glob(os.path.join(output_path, "processed_drugs_worker*.txt"))
    for filename in all_files:
        # 合并所有all_files到parser_result.txt
        with open(filename, 'r', encoding='gbk') as file:
            lines = file.readlines()
        with open(result_file_path, 'a', encoding='gbk') as file:
            file.writelines(lines)
    logging.info("合并完成！")

def drug_parser(df: pd.DataFrame, threads: int, output_dir: str, system_prompt: str):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    # 示例：保存解析结果到 txt 文件
    output_path = os.path.join(output_dir,'parser')
    os.makedirs(output_path, exist_ok=True)
    logging.info(f"解析结果保存到 {output_path}")
    main(df, threads, output_path, system_prompt)
    merge_all_data(output_path)