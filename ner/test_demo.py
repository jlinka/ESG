import os
import time
import datetime
from pprint import pprint
from collections import Counter # 计数并返回相关统计的功能

from .ner import Ner       # 使用GPU_1
from .data import DataDocument
from .data import simple_sent_cut


current_dir = os.path.dirname(os.path.realpath(__file__))
doc_dir = os.path.join(current_dir, "documents")

# 初始化相关操作类
comp = Ner()
datadocument = DataDocument()


def extract_ner(ner, docs, top_entities=100):
    """
    抽取相关文章内容
    :param docs: [sent1, ..., sentN]
    :param top_entities:
    :return:
    """
    # 全部切分,并将内容得到
    docs_process = [list(''.join(doc.split())) for index, doc in enumerate(docs)]
    # 批量预测
    ner_results = ner.extract_papers_entity(docs_process)

    # 数据解析
    _empty_count = 0

    all_doc_entities = []
    for index, result in enumerate(ner_results):

        one_doc_entity = {}

        # 存在实体, 组装这部分的序列
        if result and len(result) == 4:
            one_doc_entity["companys"] = dict(Counter(result[0]).most_common(n=top_entities))
            one_doc_entity["persons"] = dict(Counter(result[1]).most_common(n=top_entities))
            one_doc_entity["locations"] = dict(Counter(result[2]).most_common(n=top_entities))
            one_doc_entity["times"] = dict(Counter(result[3]).most_common(n=top_entities))
        elif (not result[1] or not result[0]):
            _empty_count += 1
            one_doc_entity["companys"] = {}
            one_doc_entity["persons"] = {}
            one_doc_entity["locations"] = {}
            one_doc_entity["times"] = {}
        else:   # 不存在实体,且ner结果出错
            _empty_count += 1
            one_doc_entity["companys"] = {}
            one_doc_entity["persons"] = {}
            one_doc_entity["locations"] = {}
            one_doc_entity["times"] = {}

        all_doc_entities.append(one_doc_entity)

    return all_doc_entities


'''
最原始的返回结果: 
[
    (
        ['海量证券', '湖南科技大学', '深港产学研基地深圳市智能媒体和语音重点实验室', '安徽大学', '安庆师范大学', '安徽大学', '三江学院', '深圳市智能媒体和语音重点实验室', '深圳市智能媒体和语音重点实验室', '深圳市发改委', '深圳报业集团', '科创委', '深圳证券信息智能监测企业重点实验室', '深圳市发展改革委', '国家高新技术创业服务中心', '深港产学研基地深圳市智能媒体和语音重点实验室', '深圳报业集团', '深圳证券信息有限公司', '深圳报业集团', '海量证券', '海量证券', 'FaceBook', '深圳市智能媒体和语音重点实验室', '深港产学研基地深圳市智能媒体和语音重点实验室', '深圳高交会'], 
        ['杨大明', '王昕', '刘新硕', '付磊', '杨大明', '符磊', '刘新'], 
        ['深圳市', '中国', '深圳市', '广东省', '深圳市', '广东省', '深圳市', '广东省', '深港', '深港', '深港', '深圳市', '深港', '深港', '深圳市', '广东省', '深港', '深港', '深圳市', '深圳市', '广东省', '华南地区', '日本', '美国', '北美洲', '美国', '深圳', '深圳', '深圳', '深圳', '深圳', '深圳市', '深港', '华南'],
        ['2018年度', '2006年', '2010年至今', '5年', '2013年度', '2014年度', '2013年度', '2014年度', '2015', '2017年度', '2012', '2014', '2016年7月', '2017年', '2014年7月', '2014年9月至2015年6月', '2017年至今', '2013年', '5年', '2013年', '2014年', '2011年以来', '2016年', '2014年', '2014年度', '2013年度', '2014年度', '本月', '本周', '本日', '100', '5年', '2014年', '2014年度', '2013年度', '100', '5分钟', '2003年3月', '两年内', '2004年下半年', '2014年3月24日', '1年', '3个月']
    )
]
'''


def get_entities_from_docx_and_save(task_docx, entities_save_path):
    task_doc_content = datadocument.get_content_from_docx(document_file=task_docx)
    pprint([task_doc_content])
    docs_to_entities = extract_ner(ner=comp, docs=[task_doc_content])

    # pprint(docs_to_entities)

    # with open(entities_save_path, "w", encoding="utf-8") as fw:
    #     for doc_entities in docs_to_entities:
    #         # 写入人名
    #         fw.write("人名：" + "，".join(list(set([name for name in doc_entities["doc_nr"]]))) + "\n")
    #         fw.write("地名：" + "，".join(list(set([name for name in doc_entities["doc_nt"]]))) + "\n")
    #         fw.write("\n\n")


if __name__ == '__main__':
    task_docx = os.path.join(doc_dir, "可行性研究报告-上市公司网络公开信息智能获取与深度挖掘系统-杨大明0817.docx")
    entities_save_path = os.path.join(doc_dir, str(time.time()) + "文档实体(人名地名).txt")
    get_entities_from_docx_and_save(task_docx, entities_save_path)
    # main()
    pass
