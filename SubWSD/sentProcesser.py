# coding=utf-8

# from nltk.corpus import stopwords
from parse import *
from classifySense import *
import urllib2
import json
import re

# ENGLISH_STOPWORDS = stopwords.words('english')
ENGLISH_STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                         'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn', ])
tagger = Tagger()


def tranTag(pre):
    if pre.startswith("N"):
        return 'N'
    elif pre.startswith("V"):
        return 'V'
    elif pre.startswith("R"):
        return 'ADV'
    elif pre.startswith('J'):
        return 'ADJ'
    return 'O'


def lcs(A, B):
    A = " " + A
    B = " " + B
    lengthA = len(A)
    lengthB = len(B)
    table = [[0 for i in range(lengthA)] for j in range(lengthB)]
    for i in range(1, lengthB):
        for j in range(1, lengthA):
            if B[i] == A[j]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                if table[i - 1][j] > table[i][j - 1]:
                    table[i][j] = table[i - 1][j]
                else:
                    table[i][j] = table[i][j - 1]
    return table[lengthB - 1][lengthA - 1]


class sentProcesser:

    def processSent(self, rawsent, word):
        marked = self.markKeyword(rawsent, word)
        withoutKey = self.removeKeyword((marked))
        final = self.removeStopwords(withoutKey)
        # print final
        return final

    def markKeyword(self, rawsent, word):
        if rawsent.find('<em>') == -1:
            tmp = tagger.tag(rawsent)
            withouti = [[token['word'], token['lemma'], token['pos']]
                        for token in tmp]
            found = []
            for i in range(len(withouti)):
                if withouti[i][1] == word:
                    found.append(i)
            return [withouti, found]

        withouti = rawsent.replace('<em>', ' ')
        withouti = withouti.replace('</em>', ' ')
        withouti = tagger.tag(withouti)
        withouti = [[token['word'], token['lemma'], token['pos']]
                    for token in withouti]
        pattern = re.compile("<em>([\w\s-]*)<\/em>")
        res = pattern.findall(rawsent)
        respos = 0
        found = []
        for i in range(len(withouti)):
            if withouti[i][0] == res[respos]:
                found.append(i)
                respos += 1
                if respos >= len(res):
                    break
        # print [withouti, found]
        return [withouti, found]
        # rawsent = tagger.tag(rawsent)
        # rawsent = [[token['word'], token['lemma'], token['pos']]
        #            for token in rawsent]
        # # print rawsent
        # found = []
        # for i in range(len(rawsent)):
        #     if rawsent[i][0] == '<em>':
        #         found.append(i - len(found) * 2)
        #         i += 2
        # return [withouti, found]

    def removeKeyword(self, marked):
        found = marked[1]
        withouti = marked[0]
        if found == []:
            return [withouti, 'O']
        # print marked
        try:
            pos = withouti[found[0]][2]
        except:
            pos = 'O'
        pos = tranTag(pos)
        length = len(withouti)
        for remove in found[::-1]:
            if remove >= length:
                continue
            del withouti[remove]
        return [withouti, pos]

    def removeStopwords(self, withoutKey):
        withoutstops = []
        tokens = withoutKey[0]
        for token in tokens:
            word = token[0]
            if word not in ENGLISH_STOPWORDS:
                withoutstops.append(token)
        return [withoutstops, withoutKey[1]]

    def processDic(self, dictionary, word):
        for key in dictionary.keys():
            senses = dictionary[key]
            for sense in senses:
                try:
                    sense[0] = self.processSent(sense[0], word)
                except Exception, e:
                    print repr(e)
                    continue
                # print sense
                if sense[0] == []:
                    senses.remove(sense)
        # print dictionary
        return dictionary
