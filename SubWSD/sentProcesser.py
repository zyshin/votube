# coding=utf-8

from nltk.corpus import stopwords
from parse import *
from classifySense import *
import urllib2
import json
import re

ENGLISH_STOPWORDS = stopwords.words('english')
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

