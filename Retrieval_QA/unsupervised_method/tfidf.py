import jieba
from collections import Counter, defaultdict
from gensim import corpora, models, similarities


class TfidfModel(object):
    def __init__(self, supports, stop_word=None, n_gram=None, low_freq_word=0):
        """
        jaccard 距离计算相似度
        :param supports: 知识库数据
        :param stop_word: 停用词
        :param n_gram: 支持int 和 float类型
        :param low_freq_word:
        """
        # 加载停用词
        if stop_word:
            with open(stop_word, "r", encoding="utf8") as fr:
                self.stop_words = [line.strip() for line in fr.readlines()]
        else:
            self.stop_words = []

        self.n_gram = n_gram
        self.low_freq_word = low_freq_word

        # 加载并处理知识库，便于之后快速预测
        # 给定query_id和question_id 之间的映射，query_id是对应知识库中每个问答对的问题，相似问之间也有不同的query_id。
        # 但相似问的question_id是相同的。
        self.query_to_question = {support["query_id"]: support["question_id"] for support in supports}
        # 给出question_id到answer和标准问之间的映射
        self.question_id_to_answer, self.question_id_to_question = self.get_question_to_answer(supports)
        # 取出知识库中所有的query用于之后计算相似度
        self.queries = {support["query_id"]: support["query"] for support in supports}
        # 将所有的query预先分好词，并去除停用词
        self.queries_token = {query_id: self.get_tokens(query, n_gram=n_gram)
                              for query_id, query in self.queries.items()}

        self.dictionary, self.tfidf_model, self.sim_model = self.get_tfidf_model()

    @staticmethod
    def get_question_to_answer(supports):
        """
        得到question_id到标准问和answer之间的映射
        :param supports:
        :return:
        """
        question_id_to_answer = {}
        question_id_to_question = {}
        id_flag = None
        for support in supports:
            question_id = support["question_id"]
            answer = support["answer"]
            if question_id != id_flag:
                question_id_to_question[question_id] = support["query"]
                id_flag = question_id
            if question_id_to_answer.get(question_id):
                continue
            question_id_to_answer[question_id] = answer
        return question_id_to_answer, question_id_to_question

    @staticmethod
    def get_n_gram(tokens, n_gram):
        """
        返回n_gram分词结果
        :param tokens:
        :param n_gram:
        :return:
        """
        if n_gram is None:
            return tokens

        if isinstance(n_gram, int):
            n_gram_tokens = ["".join(tokens[i: i + n_gram]) for i in range(len(tokens) - n_gram + 1)]
            new_tokens = tokens + n_gram_tokens
            return new_tokens

        if isinstance(n_gram, list):
            n_gram_tokens = ["".join(tokens[i: i + item]) for item in n_gram for i in range(len(tokens) - item + 1)]
            new_tokens = tokens + n_gram_tokens
            return new_tokens

    def get_tokens(self, sentence, n_gram=None):
        """
        分词并去除停用词
        :param sentence:
        :param n_gram:
        :return:
        """
        tokens = jieba.lcut(sentence)
        tokens = [token for token in tokens if token not in self.stop_words]
        new_tokens = self.get_n_gram(tokens, n_gram)
        return new_tokens

    @staticmethod
    def statistic_frequency(sentences):
        """
        统计训练集的词频
        :param sentences:
        :return:
        """
        word_frequency = defaultdict(int)
        for sentence in sentences:
            for token in sentence:
                word_frequency[token] += 1
        return word_frequency

    def remove_low_freq_word(self, sentences):
        """
        去除低频词
        :param sentences:
        :return:
        """
        word_frequency = self.statistic_frequency(sentences)
        new_sentence = [[token for token in sentence if word_frequency[token] > self.low_freq_word]
                        for sentence in sentences]
        return new_sentence

    def get_tfidf_model(self):
        """
        得到tfidf模型
        :return:
        """
        # 读取所有的query
        sentences = list(self.queries_token.values())
        # 去除低频词
        sentences = self.remove_low_freq_word(sentences)
        # 得到tfidf的vocab词典
        dictionary = corpora.Dictionary(sentences)
        corpus = [dictionary.doc2bow(sentence) for sentence in sentences]
        # 得到tfidf模型
        tfidf_model = models.TfidfModel(corpus)
        corpus_model = tfidf_model[corpus]
        # 得到相似度模型
        sim_model = similarities.MatrixSimilarity(corpus_model)
        return dictionary, tfidf_model, sim_model

    def sentence_to_vec(self, sentence):
        """
        将句子转换成tf-idf向量
        :param sentence:
        :return:
        """
        tokens = self.get_tokens(sentence, self.n_gram)
        bow_vec = self.dictionary.doc2bow(tokens)
        tfidf_vec = self.tfidf_model[bow_vec]
        return tfidf_vec

    def get_top_n_scores(self, sentence, n=10):
        """
        返回前n个query和对应的分数
        :param sentence:
        :param n:
        :return:
        """
        tfidf_vec = self.sentence_to_vec(sentence)
        sims = self.sim_model[tfidf_vec]
        sim_sort = sorted(list(enumerate(sims)), key=lambda item: item[1], reverse=True)
        top_n = sim_sort[:n]
        return top_n

    def get_top_n_answer(self, sentence, n=15, interval=0.2, answer_num=5):
        """
        通过给定一个间隔值来决定返回一个或多个回答
        :param sentence:
        :param n:
        :param interval:
        :param answer_num:
        :return:
        """
        question_scores = defaultdict(list)
        # 取出top n 个query
        sort_scores = self.get_top_n_scores(sentence, n)
        # 按照question_id聚合，一个question下可能会有多个query，因此也会有多个分数
        for item in sort_scores:
            question_scores[self.query_to_question[item[0]]].append(item[1])
        # 取出每个question_id对应的最大分数
        question_max_scores = [(question, max(scores)) for question, scores in question_scores.items()]
        question_max_scores = sorted(question_max_scores, key=lambda x: x[1], reverse=True)
        # 如果只有一个question_id，则直接返回该question_id对应的question 和answer
        if len(question_max_scores) == 1:
            question_id = question_max_scores[0][0]
            question_answer_pair = dict(question=self.question_id_to_question[question_id],
                                        answer=self.question_id_to_answer[question_id])
            return question_answer_pair

        # 判断其他question和最大分数的question之间的间隔，如果小于该间隔，则加入到返回的answer中
        max_scores = question_max_scores[0][1]
        question_ids = [question_max_scores[0][0]]
        for item in question_max_scores[1:]:
            if max_scores - item[1] > interval:
                break
            question_ids.append(item[0])
            if len(question_ids) >= answer_num:
                break
        question_answer_pair = [dict(question=self.question_id_to_question[question_id],
                                     answer=self.question_id_to_answer[question_id])
                                for question_id in question_ids]
        return question_answer_pair

    def max_mean_score_answer(self, sentence, n):
        """
        根据question_id对应的分数列表取平均值来决定选择哪个question对应的answer
        :param sentence:
        :param n:
        :return:
        """
        question_scores = defaultdict(list)
        # 取出top n 个query
        sort_scores = self.get_top_n_scores(sentence, n)
        # 按照question_id聚合，一个question下可能会有多个query，因此也会有多个分数
        for item in sort_scores:
            question_scores[self.query_to_question[item[0]]].append(item[1])
        # 取出每个question_id对应的平均分数
        question_mean_scores = [(question, sum(scores) / len(scores)) for question, scores in question_scores.items()]
        question_mean_scores = sorted(question_mean_scores, key=lambda x: x[1], reverse=True)
        question_id = question_mean_scores[0][0]
        question_answer_pair = dict(question=self.question_id_to_question[question_id],
                                    answer=self.question_id_to_answer[question_id])
        return question_answer_pair

    def vote_answer(self, sentence, n=1):
        """

        :param sentence:
        :param n:
        :return:
        """
        sort_scores = self.get_top_n_scores(sentence, n)
        question_ids = [self.query_to_question[item[0]] for item in sort_scores]
        question_count = Counter(question_ids)
        question_sort = sorted(question_count.items(), key=lambda x: x[1], reverse=True)
        question_id = question_sort[0][0]
        question_answer_pair = dict(question=self.question_id_to_question[question_id],
                                    answer=self.question_id_to_answer[question_id])
        return question_answer_pair