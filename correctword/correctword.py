# coding:utf-8

#%%

import re
from collections import Counter


def words(text):
    return re.findall(r'\w+', text.lower())

# 统计词频
WORDS = Counter(words(open('big.txt').read()))


def P(word, N=sum(WORDS.values())):
    """词'word'的概率"""
    return float(WORDS[word]) / N


def correction(word):
    """最有可能的纠正候选词"""
    return max(candidates(word), key=P)


def candidates(word):
    """生成拼写纠正词的候选集合"""
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words):
    """'words'中出现在WORDS集合的元素子集"""
    return set(w for w in words if w in WORDS)


def edits1(word):
    """与'word'的编辑距离为1的全部结果"""
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])     for i in range(len(word) + 1)]
    deletes    = [L + R[1:]                for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:]  for L, R in splits if len(R) > 1]
    replaces   = [L + c + R[1:]            for L, R in splits if R for c in letters]
    inserts    = [L + c + R                for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """与'word'的编辑距离为2的全部结果"""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))