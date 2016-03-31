# coding=utf-8
from subWSD import *
from sentProcesser import *
import re

# # wsd所有单词
# start = time.time()
# processAll(model)
# finish = time.time()
# print "Time: " + str(finish-start)

# # 检查前后结果是否相同
# checkAll()

# # 新建sents数据库
# cnt = 0
# for word in dicwords:
#     print word['_id']
#     cnt += 1
#     print cnt
#     if cnt < 9080:
#         continue
#     # found = subtitlesdb.find_one({'word':word['_id']})
#     # if found != None:
#     #     continue
#     if 'sents' not in word:
#         continue
#     sents = word['sents']
#     for sent in sents:
#         sent['word'] = word['_id']
#         saveSent(sent)

# 更新sents的objectID
# sents = subtitlesdb.find()
# # sents = subtitlesdb.find({'word': 'dictionary'})
# cnt = 0
# for sent in sents:
#     cnt += 1
#     print cnt
#     word = sent['word']
#     tempid = sent['_id']
#     sent['_id'] = word + '_' + \
#         sent['subtitle'].replace('.vtt', '') + '_' + str(sent['line_no'])
#     try:
#         subtitlesdb.insert_one(sent)
#     except Exception, e:
#         print repr(e)
#         print sent

#     if tempid.find('.vtt') != -1:
#         subtitlesdb.delete_one({'_id': tempid})


# 更新sents的movie
# sents = subtitlesdb.find()
# cnt = 0
# for testsent in sents:
#     cnt += 1
#     print cnt
#     testsent = setSentMovie(testsent)
#     subtitlesdb.update_one({'_id':testsent['_id']}, {'$set':{'movie':testsent['movie']}})


subtitles = getWordSents('broil')
print subtitles
print len(subtitles['sents'])

# found = dictionary.find_one({'_id': 'dictionary'})
# sents = processWord(found, model)
# for sent in sents:
#     sent['word'] = 'dictionary'

# sents = subtitlesdb.find({'word':'dictionary'})
