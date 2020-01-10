# -*- coding: utf-8 -*-
"""
   File Name：     bert_server_client
   Description :  通过调用bert服务生成句向量然后利用余弦计算相似度
   Author :       逸轩
   date：          2019/6/6

"""
import numpy as np
from bert_serving.client import BertClient

def cos_sim(vector_a, vector_b):
    """
    计算两个向量之间的余弦相似度
    :param vector_a: 向量 a
    :param vector_b: 向量 b
    :return: sim
    """
    vector_a = np.mat(vector_a)
    vector_b = np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim

def vec_sim(client, text1, text2):
    """
    传入两个文本，通过bert得到编码向量，然后调用余弦相似度计算方法得到相似度
    :param client: 客户端对象
    :param text1: 文本1
    :param text2: 文本2
    :return: sim
    """
    vecs = client.encode([text1, text2])
    sim = cos_sim(vecs[0], vecs[1])
    return sim

if __name__ == '__main__':
    # bc = BertClient(ip='')
    bc = BertClient()
    while True:
        # text1 = '男生瓜子脸适合什么发型'
        # text2 = '脸型为瓜子脸的男生怎么设计发型呢'
        text1 = input('句子1：')
        text2 = input('句子2：')
        sim_score = vec_sim(bc, text1, text2)
        print('similarity: {}'.format(sim_score))