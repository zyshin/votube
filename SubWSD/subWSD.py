# coding=utf-8
from django.conf import settings
from .settings import CREATE_SNAPSHOT, SNAPSHOT_SETTINGS
from bson.objectid import *
from classifySense import *
from sentProcesser import *
from getSubtitle import *
from gensimModel import *
import urllib2
import json
import time
import re
import subprocess

db = settings.MONGODB
dictionary = db.dict
subtitlesdb = db.sents
moviesdb = db.movies

# dicwords = dictionary.find()
sentprocesser = sentProcesser()
model = gensimModel()

# requests_cache.install_cache("subtitle_cache")


def processWord(wordjson, model):
    word = wordjson['_id']
    print 'new word:', word
    senses = wordjson['def']
    classifiedSenses = classifySenses(senses)
    dic = sentprocesser.processDic(classifiedSenses, word)
    subtitles = getSubtitles(word)
    ans = []
    onceid = []
    for subtitle in subtitles:
        tmpid = subtitle['subtitle'] + '_' + str(subtitle['line_no'])
        if tmpid in onceid:
            continue
        onceid.append(tmpid)
        sent = subtitle['sent']
        sent_ch = subtitle['sent_ch']
        try:
            sent = sentprocesser.processSent(sent, word)
        except Exception, e:
            print 'processWord:', repr(e)
            continue
        wsdans = WSD(sent, dic, model, sent_ch)
        # print wsdans[3]
        if len(wsdans) < 4:
            continue
        subtitle['sense'] = wsdans[3]
        ans.append(subtitle)
    return ans


def WSD(sent, dic, model, ch=''):
    senses = []
    allsense = []
    for key in dic.keys():
        allsense += dic[key]

    if sent[1] == 'O':
        senses = allsense
    else:
        senses = dic[sent[1]]
    if senses == []:
        senses = allsense
    sent = [token[0].lower() for token in sent[0]]
    maxsim = -1
    maxsense = ''
    maxlenchs = [max([0] + [len(s.strip()) for s in re.split(ur'[,;\(\)\[\]]', sense[1].decode('utf8')) if s.strip() and s.strip() in ch]) for sense in senses]
    for i, sense in enumerate(senses):
        sensetokens = [token[0].lower() for token in sense[0][0]]
        # if len(sent) == 0 or len(sensetokens) == 0:
        #     continue
        sim = model.n_similarity(sent, sensetokens)
        if max(maxlenchs) > 0 and i == maxlenchs.index(max(maxlenchs)):
            sim += 0.5
        # print sim
        if sim > maxsim:
            maxsim = sim
            maxsense = sense
    # print maxsense[1]
    return maxsense


def saveSent(sent, cover=False):
    word = sent['word']
    saved = subtitlesdb.find({'word': word,
                              'sent': sent['sent'], 'subtitle': sent['subtitle'],
                              'line_no': sent['line_no']})
    for save in saved:
        if cover == False:
            return
        else:
            subtitlesdb.remove(save)
    subtitlesdb.insert(sent)


def processAll(model, num=-1):
    if num == -1:
        num = 100000000
    cnt = -1
    while cnt < num:
        cnt += 1
        try:
            word = dicwords[cnt]
        except Exception, e:
            print "All:" + str(cnt + 1)
            return
        print str(cnt)
        try:
            tosave = processWord(word, model)
        except Exception, e:
            print repr(e)
            continue
        for sent in tosave:
            sent['word'] = word['_id']
            saveSent(sent, True)
    return


def getWordSents(word, limitnum=100):
    wordobj = dictionary.find_one({'_id': word})
    if not wordobj:
        r = requests.get(
        "http://dict.youdao.com/jsonapi?dicts=%7Bcount:1,dicts:%5B%5B%22collins%22%5D%5D%7D&q=" + word)
        wordobj = {'_id': word, 'def': r.json()}
        # TODO: synchronize
        dictionary.insert_one(wordobj)
        print 'new word inserted:', word
    sents = list(db.sents.find({'word': word}, limit=limitnum))
    if not sents:
        try:
            sents = processWord(wordobj, model)
        except Exception, e:
            print 'getWordSents:', repr(e)
            sents = getSubtitles(word)

        cmds = []
        for sent in sents:
            sent['_id'] = word + '_' + \
                sent['subtitle'].replace('.vtt', '') + '_' + str(sent['line_no'])
            sent['word'] = word
            sent['movie'] = sent['subtitle'][:-6]
            # extract key frame for each sent
            snapshot_settings = {
                'videofile': '%s.mp4' % sent['movie'],
                'outputfile': '%s.mp4_%d.png' % (sent['movie'], sent['line_no']),
                'time': sent['time'][1]
            }
            snapshot_settings.update(SNAPSHOT_SETTINGS)
            cmds.append('%(ffmpeg)s -i %(movie_dir)s%(videofile)s -ss %(time)s -frames:v 1 -vf scale=256:-1 -n %(snapshot_dir)s%(outputfile)s' % snapshot_settings)
            # TODO: align <em> in sent['sent'] with sent['sent_ch']
            # sent = setSentMovie(sent)
        if CREATE_SNAPSHOT:
            subprocess.Popen(';\n'.join(cmds), shell=True)

        if 0 < len(sents) <= limitnum:
            r = db.sents.insert_many(sents, ordered=False)
            print len(r.inserted_ids), 'new sents inserted for :', word

    wordobj['sents'] = sents[0:limitnum]
    return wordobj


def checkAll():
    notsame = []
    for word in dicwords:
        try:
            tempans = processWord(word, model)
        except Exception, e:
            if 'sents' in word:
                notsame.append(word['_id'])
                print notsame
            continue
        # if 'sents' not in word:
        #     continue
        sents = word['sents']

        num = len(sents)
        if num != len(tempans):
            notsame.append(word['_id'])
            print notsame
            continue

        temdic = {}
        for sent in sents:
            temdic[sent['sent']] = sent['sense']

        same = True
        for i in range(num):
            if tempans[i]['sent'] not in temdic:
                same = False
                break
            if temdic[tempans[i]['sent']] != tempans[i]['sense']:
                same = False
                break
        if same == False:
            notsame.append(word['_id'])
            print notsame


def setSentMovie(sent):
    subtitle = sent['subtitle']
    found = moviesdb.find_one(
        {'$or': [{'en_sub': {'$in': [subtitle]}}, {'dual_sub': {'$in': [subtitle]}}]})
    if found:
        imdbid = found['_id']
    else:
        imdbid = ""
    sent['movie'] = imdbid
    return sent
