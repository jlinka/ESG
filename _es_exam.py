# -*- coding: utf-8 -*-
# @Time  : 6/20/19 10:24 AM
# @Author : jlinka
# @Project : ESG
# @Desc : es全文索引简单增删改查
import os
import json
import time
from pprint import pprint
from collections import Counter

from elasticsearch import Elasticsearch

from ner.ner import Ner

cur_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(cur_dir, "data")

es = Elasticsearch()
NER = Ner(model=os.path.join(cur_dir, "ner", "models", "esg_ner_0620"))


class Data:
    def get_sents_from_txt(self, file_path):
        """

        :param file_path:
        :return:
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


class Esg:
    def __init__(self, es_host, index):
        self.index = index
        self.es = Elasticsearch([es_host])

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
            entities = NER.extract_sentences_entity(predict_process_sent)
            if len(entities[0]) != 4:
                raise Exception
        except Exception as e:
            print(e)
            entities_dict = dict(zip(keys, ([], [], [], [])))
        else:
            entities_dict = dict(zip(keys, [dict(Counter(entity).most_common(n=top_n)) for entity in entities[0]]))

        return entities_dict

    def get_paper_entities(self, sent_list, top=None):
        if isinstance(sent_list, list):
            pass
        else:
            pass
        pass

    def get_doc_from_es_by_keywords(self, keywords, index=None, field="content"):
        cur_index = index if index is not None else self.index

        cur_dsl_keys = ' '.join([word for word in keywords])
        dsl = {'query': {'match': {field: cur_dsl_keys}}}
        print(dsl)
        result = self.es.search(index=cur_index, body=dsl)
        pprint(result)
        return result


def create_index_and_insert_data():
    # es.indices.delete(index="news", ignore=[400, 404])
    # es.indices.create(index='news', ignore=400)

    with open(os.path.join(cur_dir, "data", "news.json"), "r", encoding="utf-8") as fr:
        # results = json.load(fr)
        # print(results)
        datas = [result for result in json.load(fr)]
        # print(datas)

    for index, data in enumerate(datas):
        es.create(index="news", doc_type="wechat", id=index, body=data)


def search():
    pprint("all records: {}".format(es.search(index="news")))
    # results = es.search(index='news', body={'query': {'match': {'content': '五四'}}})
    # print(results)
    # pprint("keys: {}\nsearch result: {}".format(["1939年", "五四"], ))
    pass


def test():
    text = "zn，2019年毕业于东莞理工学院，目前自2019年7月份就职于深圳市北科瑞声科技股份有限公司。" \
           "该公司位于深圳市南山区高新园南七道国家工程实验大楼。"
    esg = Esg(es_host="127.0.0.1", index="news")

    entities = esg.get_a_sent_entities(text)
    pprint(entities)

    # esg.get_doc_from_es_by_keywords(keywords=["五四", "中国青年报社"])

    # sents = [line for line in text.split("。") if line]
    # sents_to_entities = NER.extract_sentences_entity(sents)
    # pprint(sents_to_entities)


if __name__ == '__main__':
    # search()
    test()
    pass
