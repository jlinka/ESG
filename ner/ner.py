# coding:utf-8
import os
import re
import time
import pickle
import random
import argparse
import threading, multiprocessing

import numpy as np
import tensorflow as tf

from .model import BiLSTM_CRF
from .utils import str2bool, get_logger, get_entity, get_entity2, get_entity_in_esg
from .data import read_corpus, read_dictionary, tag2label, random_embedding, simple_sent_cut

current_dir = os.path.dirname(os.path.realpath(__file__))
model_dir = os.path.join(current_dir, "models")

label2tag = {}
for tag, label in tag2label.items():
    label2tag[label] = tag if label != 0 else label


def label2entity(data, labels):
    '''
    将模型输出的label和原始data结合，提取出每句的实体
    :param data:原始输入，一行一句话，每句话是每个字组成的list
    :param labels:模型输出，一行一句话，每句话每个字对应的标记
    '''
    tags = []
    length = len(data)
    for i in range(length):
        tag = [label2tag[label] for label in labels[i]]
        # company, person = get_entity2(tag, data[i][0]
        company, person, location, time = get_entity_in_esg(tag, data[i][0])

        # tags.append((company, person))
        tags.append((company, person, location, time))

    return tags


class MyThread(threading.Thread):
    # 自定义线程类，用于返回线程计算结果
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None


# class Company_ner(object):
class Ner(object):

    def __init__(self, model, gpu_str=[0]):
        self.gpus = gpu_str
        # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
        config = tf.ConfigProto(allow_soft_placement=True)
        config.gpu_options.allow_growth = True

        print(os.getcwd())
        # 使用bilstm参数
        parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
        parser.add_argument('--train_data', type=str, default='data', help='train data source')
        parser.add_argument('--batch_size', type=int, default=1000, help='#sample of each minibatch')
        parser.add_argument('--epoch', type=int, default=40, help='#epoch of training')
        parser.add_argument('--hidden_dim', type=int, default=200, help='#dim of hidden state')
        parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
        parser.add_argument('--CRF', type=str2bool, default=True,
                            help='use CRF at the top layer. if False, use Softmax')
        parser.add_argument('--lr', type=float, default=0.0001, help='learning rate')
        parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
        parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
        parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
        parser.add_argument('--pretrain_embedding', type=str, default='random',
                            help='use pretrained char embedding or init it randomly')
        parser.add_argument('--embedding_dim', type=int, default=200, help='random init char embedding_dim')
        parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
        parser.add_argument('--mode', type=str, default='demo', help='train/test/demo')
        parser.add_argument('--demo_model', type=str, default='1521112368', help='model for test and demo')
        args = parser.parse_args()

        # load字典
        output_path = os.path.join(model_dir, 'esg_ner_0623')
        word2id = read_dictionary(os.path.join(output_path, "vocab", '0618_word2id_900_char.pkl'))

        if args.pretrain_embedding == 'random':  # 随机初始化embedding
            embeddings = random_embedding(word2id, args.embedding_dim)
        else:
            embedding_path = 'pretrain_embedding.npy'
            embeddings = np.array(np.load(embedding_path), dtype='float32')

        # if args.mode != 'demo':
        #     with open(train_path, 'rb') as fr:
        #         train_data = pickle.load(fr)
        #     with open(test_path, 'rb') as fr:
        #         test_data = pickle.load(fr)
        #     test_size = len(test_data)

        ## paths setting（主要加载的模型路径）
        paths = {}
        # timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model
        if not os.path.exists(output_path): os.makedirs(output_path)
        summary_path = os.path.join(output_path, "summaries")
        paths['summary_path'] = summary_path
        if not os.path.exists(summary_path): os.makedirs(summary_path)
        model_path = os.path.join(output_path, "checkpoints/")
        if not os.path.exists(model_path): os.makedirs(model_path)
        ckpt_prefix = os.path.join(model_path, "model")
        paths['model_path'] = ckpt_prefix
        result_path = os.path.join(output_path, "results")
        paths['result_path'] = result_path
        if not os.path.exists(result_path): os.makedirs(result_path)
        log_path = os.path.join(result_path, "log.txt")
        paths['log_path'] = log_path

        self.cpu_num = multiprocessing.cpu_count()
        ckpt_file = tf.train.latest_checkpoint(model_path)
        paths['model_path'] = ckpt_file

        self.model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
        self.model.build_graph()

        print('Restore model done')
        self.saver = tf.train.Saver()
        self.sess = tf.Session(config=config)
        self.saver.restore(self.sess, ckpt_file)

    def extract_papers_entity(self, papers):
        """
        :param papers: [文章1, ... , 文章N]
        :return:
        """
        length_list = []
        papers_num = len(papers)
        sents = []
        count = 0
        for paper in papers:
            # 调用
            for sent in simple_sent_cut(paper):
                sents.append(sent)
                count += 1
            length_list.append(count)
        # 将切分后的文章句子进行分割
        sent_entity = self.extract_sentences_entity(sents)
        paper_entity = []
        start = 0
        person_, company_, location_, time_ = [], [], [], []
        for i in range(papers_num):
            for j in range(start, length_list[i]):
                company_.extend(sent_entity[j][0])
                person_.extend(sent_entity[j][1])
                location_.extend(sent_entity[j][2])
                time_.extend(sent_entity[j][3])

            paper_entity.append((company_, person_, location_, time_))
            person_, company_, location_, time_ = [], [], [], []
            start = length_list[i]
        return paper_entity

    def extract_sentences_entity(self, sents):
        """
        :param sents: [sent1, ... , sentN]
        :return: [(”句子1“[公司名], [人名], [地点], [时间])]
        """
        sentence_num = len(sents)
        # 取整
        sentence_percpu = sentence_num // self.cpu_num

        # 预测前预处理
        data = []
        result = [0] * sentence_num
        for sent in sents:
            data.append((list(sent.strip()), ['O'] * len(sent)))

        # 手动划分数据
        sentence_per_gpu = sentence_num // len(self.gpus)
        data_split_point = []
        for i in range(len(self.gpus)):
            data_split_point.append(i * sentence_per_gpu)
        data_split_point.append(sentence_num)
        #
        label_list = self.model.demo_multi(self.sess, data)

        threads = []
        for i in range(self.cpu_num):
            if i != self.cpu_num - 1:
                thread = MyThread(label2entity, args=(data[i * sentence_percpu:(i + 1) * sentence_percpu],
                                                      label_list[i * sentence_percpu:(i + 1) * sentence_percpu]))
            else:
                thread = MyThread(label2entity, args=(
                    data[i * sentence_percpu:sentence_num], label_list[i * sentence_percpu:sentence_num]))
            threads.append(thread)
            thread.start()

        for i in range(self.cpu_num):
            threads[i].join()
            if i != self.cpu_num - 1:
                result[i * sentence_percpu:(i + 1) * sentence_percpu] = threads[i].get_result()
            else:
                result[i * sentence_percpu:sentence_num] = threads[i].get_result()

        return result
