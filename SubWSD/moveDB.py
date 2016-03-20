# coding=utf-8
from pymongo import MongoClient

client = MongoClient("166.111.139.42")
client.dev.authenticate("test", "test")

dictionary = client.dev.dict

subtitlesdb = client.dev.sents

dicwords = dictionary.find()


def saveSent(sent):
    word = sent['word']
    saved = subtitlesdb.find({'word': word})
    for save in saved:
        if save['sent'] == sent['sent']:
            return
    subtitlesdb.save(sent)


for word in dicwords:
    if 'sents' not in word:
        continue
    sents = word['sents']
    for sent in sents:
        sent['word'] = word['_id']
        saveSent(sent)
