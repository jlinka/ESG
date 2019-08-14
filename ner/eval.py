import os
import xlsxwriter
from sklearn import metrics

def save_conf_mat_to_disk(confusion_matrix, labels, file_path):
    '''
    :confusion_matrix: 要保存的混淆矩阵，一定是一个方阵
    :labels: 类别标记
    :file_path: excel文件地址
    :return: 
    '''
    size = confusion_matrix.shape[0]
    book = xlsxwriter.Workbook(file_path)#创建excel文件
    sheet = book.add_worksheet('test')#创建一个表
    for i in range(1, size + 1):# 第一行和第一列为label
        sheet.write(0, i, labels[i - 1])
        sheet.write(i, 0, labels[i - 1])
    for i in range(1, size + 1):
        for j in range(1, size + 1):
            sheet.write(i, j, confusion_matrix[i - 1][j - 1])
    book.close()

def conlleval(label_predict, label_path, metric_path):
    """

    :param label_predict:
    :param label_path:
    :param metric_path:
    :return:
    """
    eval_perl = "./conlleval_rev.pl"
    label_true, label_pred, labels = [], [], [0, 'B-company_name', 'I-company_name', 'B-person_name', 'I-person_name']
    with open(label_path, "w", encoding='utf8') as fw:
        line = []
        for sent_result in label_predict:
            for char, tag, tag_ in sent_result:#tag是真实，tag_是预测的
                tag = '0' if tag == 'O' else tag
                # char = char.encode("utf-8")
                line.append("{} {} {}\n".format(char, tag, tag_))
                label_true.append(tag)
                label_pred.append(tag_)
            line.append("\n")
        fw.writelines(line)
    conf_mat = metrics.confusion_matrix(label_true, label_pred, labels)
    save_conf_mat_to_disk(conf_mat, labels, label_path + '_conf_mat.xls')
    os.system("perl {} < {} > {}".format(eval_perl, label_path, metric_path))
    with open(metric_path) as fr:
        metric = [line.strip() for line in fr]
    return metric

    