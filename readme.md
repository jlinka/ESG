# 项目概要
    ESG项目: 命名实体识别（人名、地名、公司名、机构名、时间）-> 关键字组合 -> es全文索引获取相关新闻

## 主要代码逻辑

- 第一步: 文档实体抽取
- 第二步: 实体组装elasticsearch DSL查询语句进行记录查询
- 第三步: 保存相关记录

## 项目依赖
- 库依赖
    - python ==>3.5
    - numpy ==>1.14.2
    - tensorflow-gpu ==>1.2.1 或 tensorflow ==>1.2.1
    - elasticsearch 
    - python-docx ==> 0.8.10   
    - scikit-learn ==> 0.21.1

## 目录结构

- data.py: 封装的主要工具类, 具体使用见代码
- esg.py: **主要函数,组装了实体抽取\实体topn排序\es关键词查询及结果保存**
- ner: **直接使用就可以了,这不是重点**
    - models
        - esg_ner_0623: esg最新的模型，包含四类命名实体识别(公司名\人名\地名\时间)
    - data.py： ner中对训练、预测处理的函数
        1. 这里只使用了简易的分句方法：用。?!进行分句，可以替换，输入的句子最大长度越短，越有利于提高模型的并行程度
    - model.py： bilstm神经网络结构
    - ner.py： ner模型预测的主要文件
        1. ner.py文件中Company_ner类的__init__函数第一行，0,1,2...表示显卡的编号
    - utils.py： 工具脚本，包括相关的组装
    - eval.py： 主要验证函数

## 简单测试

运行命令:
- python esg.py 文件中test()函数
- python esg.py 
    - 结果保存: /ESG/data/tmp, 相对路径中可以查阅到内容
    - tmp最重要文件:
        - 相关实体及搜索参数综合.txt: 包含详细的说明
        - 其他文件: 主要是原始新闻和关联新闻的保存

