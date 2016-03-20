# coding=utf-8
import string


def splitSense(sense):
    length = len(sense)
    lastpoint = 0
    # print sense
    for i in range(length):
        if sense[i] not in string.printable:
            if lastpoint == 0:
                lastpoint = i - 1
            if sense[lastpoint] == '(':
                lastpoint = lastpoint - 1
            english = sense[0:lastpoint + 1]
            chinese = sense[lastpoint + 1:length]
            ans = [english, chinese]
            return ans
        else:
            if sense[i] in ['.', '?', '!']:
                lastpoint = i
    return [sense, sense]


def classifySenses(dic):
    word = dic['simple']['query']
    collins = dic["collins"]
    collins_entries = collins["collins_entries"]
    ans = {}
    ans['N'] = []
    ans['V'] = []
    ans['ADJ'] = []
    ans['ADV'] = []
    ans['O'] = []
    lastenglish = ''
    No = -1
    for entry in collins_entries:
        entries = entry["entries"]["entry"]
        for sense in entries:
            No += 1
            for tran_entry in sense["tran_entry"]:
                try:
                    pos = tran_entry["pos_entry"]["pos"]
                    chinese = tran_entry["tran"].encode("utf-8")
                    chinese = chinese.replace("<b>", "")
                    chinese = chinese.replace("</b>", "")
                except Exception, e:
                    continue

                examplesent = []
                try:
                    examplesents = tran_entry["exam_sents"]['sent']
                    for exam_sent in examplesents:
                        examplesent.append(exam_sent["eng_sent"])
                except Exception, e:
                    examplesent = []

                chinese = chinese.strip()
                if chinese[0] not in string.printable:
                    continue

                try:
                    english, chinese = splitSense(chinese)
                except Exception, e:
                    # print chinese
                    continue

                english = english.strip()
                if english == "":
                    continue

                if english.lower().startswith(word + " is also an adjective") \
                        or english.lower().startswith(word + " is also an adverb") \
                        or english.lower().startswith(word + " is also a noun") \
                        or english.lower().startswith(word + " is also a verb"):
                    english = lastenglish

                chinese = [english, chinese]

                chinese.append(examplesent)
                chinese.append(No)
                if pos[0] == "N":
                    ans['N'].append(chinese)
                elif pos[0] == "V":
                    ans['V'].append(chinese)
                elif pos == "ADJ":
                    ans['ADJ'].append(chinese)
                elif pos == "ADV":
                    ans['ADV'].append(chinese)
                else:
                    ans['O'].append(chinese)
                lastenglish = chinese[0]
    return ans
