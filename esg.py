# -*- coding: utf-8 -*-
# @Time  : 6/20/19 10:24 AM
# @Author : jlinka
# @Project : ESG
# @Desc : 句子实体抽取\实体排序\es数据库关键字检索
import os
import json
import time
from pprint import pprint
from collections import Counter
# import proxyTool
from elasticsearch import Elasticsearch

from ner.ner import Ner

# 获取当前项目绝对路径
cur_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(cur_dir, "data")


# es = Elasticsearch()

class Data:
    def get_sents_from_txt(self, file_path):
        """
        返回句子list, txt每行内容为一个句子
        :param file_path:
        :return: sents_list
        """
        sents = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as fr:
                for line in fr.readlines():
                    if line != '\n':
                        sents.append(line.strip())
        else:
            print('please check {} is exits'.format(file_path))
        return sents

    def save_related_news(self, save_dir, title=None, contents=None, batch_news=None):
        """
        保存关联新闻
        模式一: 批量保存
        模式二: 单新闻保存
        :save_dir: 保存目录, str
        :title: 保存标题即文件名, str
        :contents: 保存内容, str
        :batch_news: [[title1, content1],...,[titleN, contentN]]
        """

        if title is not None and contents is not None and batch_news is None:
            with open(os.path.join(save_dir, title + ".txt"), 'w', encoding='utf-8') as fw:
                fw.write('标题: ' + title + '\n\n')
                fw.write('正文: ' + contents)
        elif batch_news is not None:
            for title, content in batch_news:
                with open(os.path.join(save_dir, title + ".txt"), 'w', encoding='utf-8') as fw:
                    fw.write('标题: ' + title + '\n\n')
                    fw.write('正文: ' + content)
        else:
            print("please ckeck your parms")

    def save_to_txt(self, save_path, content_list):
        """
        保存list内容到txt文件中
        """
        if isinstance(content_list, list) and len(content_list):
            with open(save_path, 'w', encoding='utf-8') as fw:
                for content in content_list:
                    fw.write(content + '\n')
        else:
            pass


class Esg:
    def __init__(self, es_host, index,
                 ner_model_path=os.path.join(cur_dir, "ner", "models", "esg_ner_0620")):
        """

        :param es_host: es host地址
        :param index: es 索引名
        :param ner_model_path: ner 模型名, 基本使用默认路径,如果有新模型再自适应修改
        """
        self.index = index
        self.es = Elasticsearch([es_host])
        self.ner_model = Ner(model=ner_model_path)

    def get_a_sent_entities(self, sent, top_n=10):
        """
        抽取句子中的命名实体（公司名、人名、地点名、时间）
        :param sent: str or [sent]
        :param top_n: 默认返回前10个命名实体
        :return: dict: {"company": [], "person": [], "location": [], "time": []}
        """
        keys = ["company", "person", "location", "time"]

        try:
            predict_process_sent = sent if isinstance(sent, list) and len(sent) == 1 else [sent]
            entities = self.ner_model.extract_sentences_entity(predict_process_sent)
            if len(entities[0]) != 4:
                raise Exception
        except Exception as e:
            print(e)
            entities_dict = dict(zip(keys, ([], [], [], [])))
        else:
            entities_dict = dict(zip(keys, [dict(Counter(entity).most_common(n=top_n)) for entity in entities[0]]))

        return entities_dict

    def get_paper_entities(self, sent_list, top=None):
        pass

    def get_doc_from_es_by_keywords(self, keywords, index=None, field="content"):
        """

        :param keywords:
        :param index:
        :param field:
        :return:
        """
        cur_index = index if index is not None else self.index

        cur_dsl_keys = ' '.join([word for word in list(set(keywords))])
        dsl = {'query': {'match': {field: cur_dsl_keys}}}
        result = self.es.search(index=cur_index, body=dsl)
        return result


def test():
    # data 工具类
    data_tool = Data()
    esg = Esg(es_host="192.168.0.27:9200", index="company_article_map_test")
    # 抽取新闻路径
    test_new = os.path.join(data_dir, '如封杀华为中兴 欧洲建5G要多花4287亿晚一年半.txt')
    # 新闻转sent_list
    sents = data_tool.get_sents_from_txt(test_new)
    sent_to_text = ",".join(sents)
    # 新闻抽取全部实体
    all_entities_dict = esg.get_a_sent_entities(sent_to_text)

    # 抽取实体去topN
    top_n = 10
    top_keywords = []
    # 规整相关实体
    for type, entities_dict in all_entities_dict.items():
        if len(entities_dict) >= 0 and isinstance(entities_dict, dict):
            # 获取top n个实体
            entity_count_list = sorted(entities_dict.values(), reverse=True)
            top_entity_count_list = entity_count_list[:top_n] if len(entity_count_list) >= top_n else entity_count_list
            # 反转字典
            count_entity_dict = {}
            for entity, count in entities_dict.items():
                if count not in count_entity_dict.keys():
                    count_entity_dict[count] = [str(entity).strip()]
                else:
                    count_entity_dict[count].append(str(entity).strip())
            # 取top个实体
            for top_index in top_entity_count_list:
                for _entity in count_entity_dict[top_index]:
                    top_keywords.append(_entity)

    pprint(top_keywords)

    es_search_result = esg.get_doc_from_es_by_keywords(keywords=top_keywords)
    # 原始新闻参数简单组装
    content_list = []
    all_news = [["原始新闻:" + sents[0], ",".join(sents[1:])]]
    content_list.append("原始新闻: {}\n".format(sents[0]))
    content_list.append("全部实体及频率: \nPerson: {}\nCompany: {}\nLocation: {}\nTime: {}".format(all_entities_dict["person"],
                                                                                            all_entities_dict[
                                                                                                "company"],
                                                                                            all_entities_dict[
                                                                                                "location"],
                                                                                            all_entities_dict["time"]))
    content_list.append("top {}\t实体: {}".format(top_n, " ".join(top_keywords) + '\n'))
    content_list.append("\n关联新闻如下:\n")

    # es关联新闻梳理并且保存到响应文件中
    for hits_value in es_search_result["hits"]["hits"]:
        # hits_value 为新闻相关list
        score = hits_value['_score']
        title = str(hits_value['_source']['title']).strip()
        source = str(hits_value['_source']['source']).strip()
        content = str(hits_value['_source']['content']).strip()
        print("关联新闻标题: {}\t得分: {}\t来源: {}".format(title, score, source))
        all_news.append(["关联新闻:" + title, content])
        content_list.append("标题: {}\tEs搜索得分:{}".format(title, score))
    # 临时保存路径
    cur_new_dir = os.path.join(data_dir, 'tmp')
    # 保存查询得到的新闻
    data_tool.save_related_news(save_dir=cur_new_dir, batch_news=all_news)
    data_tool.save_to_txt(save_path=os.path.join(cur_new_dir, "相关实体及搜索参数综合.txt"), content_list=content_list)


if __name__ == '__main__':
    test()
    pass
