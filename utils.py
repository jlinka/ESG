# -*- coding: utf-8 -*-
# @Time  : 6/20/19 11:29 AM
# @Author : jlinka
# @Project : ESG
# @Desc :

import json
import ast


class Data:
    def txt_to_json(self, txt_file_path, json_file_path):
        with open(txt_file_path, "r", encoding="utf-8") as fr:
            # results = [json.loads(line.strip()) for line in fr.readlines() if line != '\n']
            # json形式的'{}'字符串转dict
            results = [ast.literal_eval(line.strip()) for line in fr.readlines() if line != '\n']

        with open(json_file_path, "w", encoding="utf-8") as fw:
            json.dump(results, fw, ensure_ascii=False)


if __name__ == '__main__':
    Data.txt_to_json("./data/news.txt", "./data/news.json")
    pass
