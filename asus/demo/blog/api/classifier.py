# coding=utf-8
import csv
import jieba
import pickle
import gensim
import numpy as np
from sklearn import metrics
import os
from ..settings import APP_STATIC

w2v_model = gensim.models.Word2Vec.load(os.path.join(APP_STATIC, 'pickles/w2v_model_size100_window5_mincount1'))

class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        self.dim = len(list(word2vec.values())[0])

    def fit(self, X, y):
        return self

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec]
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])
    
vectorizer = MeanEmbeddingVectorizer(dict(zip(w2v_model.wv.index2word, w2v_model.wv.syn0)))
w2v_svrs = pickle.load(open(os.path.join(APP_STATIC, 'pickles/w2v_svrs.p'),'rb'))

dummy = jieba.cut('',cut_all = False)

def jieba_cut(sentence):
    return [word for word in jieba.cut(sentence, cut_all = False) if word != ' ']

def w2v_svr_score(cut):
    clist = list(cut)
    filtered_list = []
    for w in clist:
        try:
            s = w2v_model.wv[w]
            filtered_list.append(w)
        except KeyError:
            continue
    return np.mean([svr.predict(X=list(vectorizer.transform([list(cut)]))) for svr in w2v_svrs], axis=0)

randomForest_clf = pickle.load(open(os.path.join(APP_STATIC, 'pickles/TFIDF_RandomForestClassifier.pkl') ,'rb'))
linearSVC_clf = pickle.load(open(os.path.join(APP_STATIC, 'pickles/LinearSVC_Classifier.pkl') ,'rb'))
naive_bayes_clf = pickle.load(open(os.path.join(APP_STATIC, 'pickles/Naive_bayes_Classifier.pkl') ,'rb'))
decisionTree_clf = pickle.load(open(os.path.join(APP_STATIC, 'pickles/DecisionTree_Classifier.pkl') , 'rb'))


from enum import Enum
class states(Enum):
    IDLE = 0
    RUNNING = 1

w2v_svr_pos_threshold = -0.2
w2v_svr_neg_threshold = -0.45

def score2text(score):
    if score > w2v_svr_pos_threshold:
        return '滿意'
    elif score < w2v_svr_neg_threshold:
        return '不滿意'
    else:
        return '中立'

def classifier(sentence_cut):
    classifier_dict = {}
    # bag of word and classifier
    conbine_sentence = [' '.join(sentence_cut)]
    # LinearSVC
    # if linearSVC_clf.predict(conbine_sentence)[0] == 1:
    #     print('LinearSVC: \t', '滿意\t')
    # else:
    #     print('LinearSVC: \t', '不滿意')

    # # Naive_Bayes
    # if naive_bayes_clf.predict(conbine_sentence)[0] == 1:
    #     print('Naive_Bayes: \t', '滿意\t', naive_bayes_clf.predict_proba(conbine_sentence))
    # else:
    #     print('Naive_Bayes: \t', '不滿意\t', naive_bayes_clf.predict_proba(conbine_sentence))
            
    # # RandomForest
    # if randomForest_clf.predict(conbine_sentence)[0] == 1:
    #     print('RandomForest: \t', '滿意\t', randomForest_clf.predict_proba(conbine_sentence))
    # else:
    #     print('RandomForest: \t', '不滿意\t', randomForest_clf.predict_proba(conbine_sentence))
            
    # # DecisionTree
    # if decisionTree_clf.predict(conbine_sentence)[0] == 1:
    #     print('DecisionTree: \t', '滿意\t', decisionTree_clf.predict_proba(conbine_sentence))
    # else:
    #     print('DecisionTree: \t', '不滿意\t', decisionTree_clf.predict_proba(conbine_sentence))
    classifier_dict['linearSVC_clf'] = int(linearSVC_clf.predict(conbine_sentence)[0])

    classifier_dict['naive_bayes_clf'] = int(naive_bayes_clf.predict(conbine_sentence)[0])
    classifier_dict['naive_bayes_proba'] = naive_bayes_clf.predict_proba(conbine_sentence).tolist()

    classifier_dict['randomForest_clf'] = int(randomForest_clf.predict(conbine_sentence)[0])
    classifier_dict['randomForest_proba'] = randomForest_clf.predict_proba(conbine_sentence).tolist()

    classifier_dict['decisionTree_clf'] = int(decisionTree_clf.predict(conbine_sentence)[0])
    classifier_dict['decisionTree_proba'] = decisionTree_clf.predict_proba(conbine_sentence).tolist()
    return classifier_dict


window=3

sentence = ''
dialogue = []
def verify(sentence):
    result = {}
    dialogue.append(sentence)
    dialogue_in_window=''
    whole_dialogue = ''
            
    for d in dialogue[window *- 1:]:
        dialogue_in_window += d + ' '
               
    for d in dialogue:
        whole_dialogue += d + ' '

    sentence_cut = jieba_cut(sentence)
    window_cut = jieba_cut(dialogue_in_window)
    dialogue_cut = jieba_cut(whole_dialogue)
            
    sentence_score = w2v_svr_score(sentence_cut)
    window_score = w2v_svr_score(window_cut)
    dialogue_score = w2v_svr_score(dialogue_cut)
            
    sen_text = score2text(sentence_score)
    win_text = score2text(window_score)
    dia_text = score2text(dialogue_score)
            
    print(sentence_cut)
    print(window_cut)
    print(dialogue_cut)
    print('本句情緒分數:\t', sentence_score, '\t', sen_text)
    print('Window內情緒分數:\t', window_score, '\t', win_text)
    print('完整對話情緒分數:\t', dialogue_score, '\t', dia_text)
    print()
    # print("本句滿意度: \t\t 不滿意機率 \t 滿意機率")
    # classifier(sentence_cut)
    # print()
    # print("Window內滿意度: \t\t 不滿意機率 \t 滿意機率")
    # classifier(window_cut)
    # print()
    # print("完整對話滿意度: \t\t 不滿意機率 \t 滿意機率")
    # classifier(dialogue_cut)

    result['sentence_score'] = sentence_score.tolist()
    result['window_score'] = window_score.tolist()
    result['dialogue_score'] = dialogue_score.tolist()

    result['sentence_classifier'] = classifier(sentence_cut)
    result['windows_classifier'] = classifier(window_cut)
    result['dialogue_classifier'] = classifier(dialogue_cut)
    print(result)
    return result
