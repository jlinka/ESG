# -*- coding: utf-8 -*-
# @Time  : 6/19/19 2:12 PM
# @Author : jlinka
# @Project : ESG
# @Desc :
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch import helpers

num = 0
body = []
# es_hosts = ["192.168.0.27:9200"]    # 175服务器没有列入192网段，所以不能使用该方式连接
es_hosts = ["172.16.5.37:9200"]  # 175服务器没有列入192网段，所以不能使用该方式连接

es = Elasticsearch(es_hosts)
helpers.bulk(es, body)


def main():
    es = Elasticsearch(es_hosts)
    helpers.bulk(es, body)
    sql = {"min_score": 3, "query": {"bool": {"should": []}}}
    keywords = ['安全事故', '公司', '荣盛']
    for i in keywords:
        res = {}
        res = {"constant_score": {"filter": {"match_phrase": {"title": i}}, "boost": 1}}
        sql["query"]['bool']['should'].append(res)
    # sql = {"min_score":2,"query": {"bool": {"should":[{"constant_score":{"filter": {"match_phrase": {"title": "安全"}},"boost": 1}},{"constant_score": {"filter": {"match_phrase": {"title": "安全事故"}},"boost": 1}}]}}}

    res = es.search(index='company_article_map_web', body=sql)
    pprint(res)


if __name__ == '__main__':
    main()
