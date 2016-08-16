from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView

from .settings import SNAPSHOT_FROM_CACHE
import json
from itertools import chain
from datetime import datetime
from SubWSD.subWSD import getWordSents
from SubWSD.classifySense import splitSense, classifySenses
from SubWSD.sentProcesser import lcs
from SubWSD.subWSD import sentprocesser, dictionary, model, WSD

from pymongo import ReturnDocument
db = settings.MONGODB

zero_time = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')


from time import clock


def timeit(func):
    def __decorator(*args, **kwags):
        start = clock()
        # recevie the native function call result
        result = func(*args, **kwags)
        finish = clock()
        span = int((finish - start) * 1000)
        if span > 500:
            print '[DEBUG] timeit: ', func.__name__, span, 'ms'
        return result  # return to caller
    return __decorator


class MyView(View):

    def get(self, request, *args, **kwargs):
        word = request.GET.get('word', '').strip()
        r = JsonResponse(getWordSents(word))
        r = self.__cors(r)
        return r

    @staticmethod
    def __cors(r):
        r['Access-Control-Allow-Origin'] = '*'
        r['Access-Control-Allow-Credentials'] = 'true'
        r['Access-Control-Expose-Headers'] = 'Access-Control-Allow-Origin, Access-Control-Allow-Credentials'
        return r


class PageView(TemplateView):

    @staticmethod
    @timeit
    def __getWordSents(word):
        return getWordSents(word)

    @staticmethod
    @timeit
    def __wsd(word_object, context):
        try:
            word = word_object['_id']
            senses = word_object['def']
            classifiedSenses = classifySenses(senses)
            dic = sentprocesser.processDic(classifiedSenses, word)
            sent = sentprocesser.processSent(context, word)
            wsdans = WSD(sent, dic, model)
            print 'WSD result:', wsdans[3]
        except Exception, e:
            print repr(e)
            print '__wsd error'
            return 0
        return wsdans[3]

    @staticmethod
    @timeit
    def __get_word(word):
        # TODO: move into templates
        try:
            w = word['def']['simple']['word'][0]
        except Exception, e:
            print repr(e)
            w = {}
        ukphone = w.get('ukphone', w.get('usphone', ''))
        ukspeech = w.get('ukspeech', w.get('usspeech', ''))
        usphone = w.get('usphone', w.get('ukphone', ''))
        usspeech = w.get('usspeech', w.get('ukspeech', ''))
        try:
            forms = ', '.join([o['word'] for o in word['def']['collins']['collins_entries'][
                              0]['basic_entries']['basic_entry'][0]['wordforms']['wordform']])
        except Exception, e:
            print repr(e)
            forms = ''
        try:
            meanings = list(chain(*[[te['tran_entry'][0] for te in e['entries']['entry']]
                                    for e in word['def']['collins']['collins_entries']]))
            meanings = [m for m in meanings if m.get('tran')]
            for i, m in enumerate(meanings):
                m['id'] = 'sense%d' % (i + 1)
                m['tran_cn'] = splitSense(m['tran'])[1]
                m['tran_en'] = m['tran'].replace(m['tran_cn'], '').strip()
            # TODO: filter meanings
        except Exception, e:
            print repr(e)
            meanings = []
        return {
            'word': word['_id'],
            't': word.get('t', False),
            'g': word.get('g', False),
            'ukphone': ukphone,
            'ukspeech': ukspeech,
            'usphone': usphone,
            'usspeech': usspeech,
            'forms': forms,
            'meanings': meanings,
            'tran': word.get('tran', '(No definition found)'),
            'raw_word': word
        }

    @staticmethod
    @timeit
    def __get_clips(word):
        # pertain clips with movie downloads
        word['sents'] = [s for s in word['sents'] if s['movie']]
        for s in word['sents']:
            s['id'] = s['_id']
            times = [(datetime.strptime(t, '%H:%M:%S.%f') -
                      zero_time).total_seconds() for t in s['time']]
            s['time'] = times
            s['start'] = max((times[0] + times[1]) / 2, times[1] - 3)
            s['end'] = min((times[2] + times[3]) / 2, times[2] + 1)
            # s['start'] = start.strftime('%H:%M:%S.%f')[:-3]
            # s['end'] = end.strftime('%H:%M:%S.%f')[:-3]
            s['length'] = s['end'] - s['start']
            s['morph'] = s['line'][s['line'].find(
                '<em>') + 4:s['line'].find('</em>')]
        return word['sents']

    @staticmethod
    @timeit
    def __get_movies(word):
        ids = list(set([s['movie'] for s in word['sents']]))
        d = {o['_id']: o for o in db.movies.find({'_id': {'$in': ids}, 'videofile': {'$ne': ''}})}
        for s in word['sents']:
            s['movie'] = d.get(s['movie'], {})
            if SNAPSHOT_FROM_CACHE and s['movie'].get('videofile'):
                s['snapshot'] = '%s_%d.png' % (
                    s['movie']['videofile'], int(s['time'][1]))
        for m in d.itervalues():
            assert m['videofile']
            # convert to safe css class name
            m['id'] = ''.join(
                [c for c in m['_id'] if c.islower() or c.isdigit()])
            #m['rating'] = float(m['rating'])
            m['omdb']['imdbRating'] = float(m['omdb']['imdbRating'])
            m['omdb']['imdbVotes'] = int(
                m['omdb']['imdbVotes'].replace(',', ''))
            if 'poster' in m:
                m['poster_cached'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + \
                    m['poster'].split('/')[-1]
            if 'Poster' in m['omdb']:
                m['poster_cached2'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + \
                    m['omdb']['Poster'].split('/')[-1]
        return d.values()

    @staticmethod
    def __line_length(line):
        ss = line.split()
        times = [ss[0], ss[2]]
        times = [(datetime.strptime(t, '%H:%M:%S.%f') -
                  zero_time).total_seconds() for t in times]
        return times[1] - times[0]

    @classmethod
    @timeit
    def __distinct_clips(cls, clips):
        # filter context['clips'] with same videofile and 90%-similar line
        st, num = 0, len(clips)
        toremove = []
        while st < num:
            sentA = clips[st]['line'][clips[st]['line'].find('\n') + 1:]
            for i in range(st):
                if clips[st]['movie']['videofile'] != clips[i]['movie']['videofile']:
                    continue
                sentB = clips[i]['line'][clips[i]['line'].find('\n') + 1:]
                cover = lcs(sentA, sentB)
                ratio = 1.0 * cover / max([len(sentA), len(sentB)])
                if ratio > 0.9:
                    tmp = clips[st]
                    if cls.__line_length(tmp['line']) > cls.__line_length(clips[i]['line']):
                        tmp = clips[i]
                    toremove.append(tmp)
                else:
                    sentA = clips[st]['sent'].replace(
                        '<em>', '').replace('</em>', '')
                    sentB = clips[i]['sent'].replace(
                        '<em>', '').replace('</em>', '')
                    if sentA.strip() == sentB.strip():
                        toremove.append(clips[st])
            st += 1
        r = [c for c in clips if c not in toremove]
        if len(r) < len(clips):
            print len(clips) - len(r), 'duplicated clips removed'
        return r

    @timeit
    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        if 'visited' not in self.request.session:
            self.request.session['visited'] = str(datetime.now())
        context['is_plugin'] = 'plugin' in self.request.GET
        context['SNAPSHOT_FROM_CACHE'] = SNAPSHOT_FROM_CACHE

        word = self.request.GET.get('word', '').strip() or 'default'
        r = self.__getWordSents(word)
        context['word'] = self.__get_word(r)
        context['clips'] = self.__get_clips(r)
        context['movies'] = self.__get_movies(r)
        context['clips'] = [c for c in context['clips'] if c[
            'movie'].get('videofile')]    # pertain clips with movie file
        context['clips'] = [c for c in context['clips']
                            if c['length'] < 30]    # pertain short clips
        context['clips'] = self.__distinct_clips(context['clips'])

        # sort context['clips']:
        # 1. by sense 123
        # 2. by votes
        # 3. by length of the occurrence line
        # 4. by reversed clip length
        # 5. by views
        context['clips'].sort(key=lambda c: (-c.get('sense', 0), c.get('votes', 0), int(
            self.__line_length(c['line']) / 2), -int(c['length'] / 2), c.get('views', 0)), reverse=True)
        context['movies'].sort(key=lambda m: -(m.get('t', 0) + m.get('g', 0)))

        if context['clips']:
            clip_id = self.request.GET.get('clip_id')
            clip_ids = [c['id'] for c in context['clips']]
            index = clip_ids.index(clip_id) if clip_id in clip_ids else 0
            context['active_clip'] = context['clips'][index]

        if context['movies']:
            movie_id = self.request.GET.get('movie_id', '')
            if movie_id:
                context['clips'] = [c for c in context[
                    'clips'] if c['movie']['id'] == movie_id]
            context['movies'] = [
                {'id': '', 'title': 'All Movies'}] + context['movies']
            ids = [m['id'] for m in context['movies']]
            context['active_movie'] = context['movies'][ids.index(movie_id)]

        if context['word']['meanings']:
            sense_id = self.request.GET.get('sense_id', '')
            word_context = self.request.GET.get('context')
            if not sense_id and word_context:
                sense_id = 'sense%d' % (self.__wsd(context['word']['raw_word'], word_context) + 1)
            if sense_id:
                context['clips'] = [c for c in context['clips']
                                    if c.get('sense', 0) == int(sense_id[5:]) - 1]
                if clip_id not in clip_ids and context['clips']:
                    index = 0
                    context['active_clip'] = context['clips'][index]
                    context['next_clip'] = context['clips'][
                        (index + 1) % len(context['clips'])]
            meanings = [{'id': '', 'tran_cn': 'All Meanings'}] + \
                context['word']['meanings']
            for i, m in enumerate(meanings[1:]):
                m['index'] = '%d.' % (i + 1)
            ids = [m['id'] for m in meanings]
            index = ids.index(sense_id)
            context['active_sense'] = {
                'current': meanings[index],
                'previous': meanings[index - 1],
                'next': meanings[(index + 1) % len(meanings)],
            }
            # TODO: skip empty previous/next

        return context

    def post(self, request):
        clip_id = request.POST.get('clip_id')
        sessionid = request.POST.get('sessionid', 'unknown')
        pid = request.POST.get('pid', 'unknown')
        if clip_id:
            print 'vote on %s by %s (%s)' % (clip_id, sessionid, pid)
            clip = db.sents.find_one_and_update(
                {'_id': clip_id}, {'$inc': {'votes': 1}}, return_document=ReturnDocument.AFTER)
            return HttpResponse(str(clip['votes']))


class AnalyticView(View):

    def get(self, request, *args, **kwargs):
        clip_id = request.GET.get('clip_id')
        clip = db.sents.find_one_and_update(
            {'_id': clip_id}, {'$inc': {'views': 1}}, return_document=ReturnDocument.AFTER)
        return HttpResponse(str(clip['views']))
