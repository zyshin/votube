# coding=utf-8
from subWSD import *


GT = dictionary.find({'$or': [{'g': True}, {'t': True}]})
# GT = dictionary.find({'g':True})
# GT = dictionary.find({'t':True})
# GT = dictionary.find({'_id':'slew'})
ED = []

# GT = GT[0:100]

best = {'Our': 0, 'PosF': 0, 'F': 0, 'All': 0}
worst = {'Our': 0, 'PosF': 0, 'F': 0, 'All': 0}


def foundFirst(senses):
    first = {}
    zero = []
    for key in senses.keys():
        min = []
        for sense in senses[key]:
            if min == [] or sense[3] < min[3]:
                min = sense
            if zero == [] or sense[3] < zero[3]:
                zero = sense
        first[key] = min
    first['O'] = zero
    # print senses
    # print first
    return first


def updateCnt(wsdans, firsts, sense, pos, ifworst):
    if wsdans[3] == sense[3]:
        best['Our'] += 1
        if ifworst:
            worst['Our'] += 1
    if firsts[pos] == []:
        pos = 'O'
    if firsts[pos][3] == wsdans[3]:
        best['PosF'] += 1
        if ifworst:
            worst['PosF'] += 1
    if firsts['O'][3] == wsdans[3]:
        best['F'] += 1
        if ifworst:
            worst['F'] += 1
    best['All'] += 1
    if ifworst:
        worst['All'] += 1

for word in GT:
    if word['_id'] in ED:
        continue
    print word['_id']
    ED.append(word['_id'])
    try:
        senses = classifySenses(word['def'])
        dic = sentprocesser.processDic(senses, word['_id'])
    except Exception, e:
        print repr(e)
        continue

    firsts = foundFirst(senses)
    for dicpos in senses:
        possense = senses[dicpos]
        possenselength = len(possense)
        for sense in possense:
            example = sense[2]
            if example != []:
                try:
                    sent = sentprocesser.processSent(example[0], word['_id'])
                except Exception, e:
                    print 'processSent:', repr(e)
                    continue
                try:
                    wsdans = WSD(sent, dic, model)
                except Exception, e:
                    print 'WSD:', repr(e)
                    continue

                sentpos = tranTag(sent[1])
                if (possenselength == 1) and (dicpos != 'O'):
                    updateCnt(wsdans, firsts, sense, sentpos, False)
                else:
                    updateCnt(wsdans, firsts, sense, sentpos, True)
                print example[0]
                print '(', dicpos, ',', sentpos, ',', possenselength, ')', sense[1], '|', wsdans[1]
                print 'best:', best
                print 'worst:', worst

print 'best: ', 'F-', 1.0*best['F']/best['All'], ' PosF-', 1.0*best['PosF']/best['All'], ' Our-', 1.0*best['Our']/best['All']
print 'worst: ', 'F-', 1.0*worst['F']/worst['All'], ' PosF-', 1.0*worst['PosF']/worst['All'], ' Our-', 1.0*worst['Our']/worst['All']

