from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView

import json
from itertools import chain
from datetime import datetime
from SubWSD.subWSD import getWordSents
from SubWSD.classifySense import splitSense
from SubWSD.sentProcesser import lcs

from pymongo import MongoClient, ReturnDocument
db = MongoClient('166.111.139.42').dev
db.authenticate('test', 'test')

zero_time = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')


class MyView(View):

    def get(self, request, *args, **kwargs):
        word = request.GET.get('word', '')
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
            forms = ', '.join([o['word'] for o in word['def']['collins']['collins_entries'][0]['basic_entries']['basic_entry'][0]['wordforms']['wordform']])
        except Exception, e:
            print repr(e)
            forms = ''
        try:
            meanings = list(chain(*[[te['tran_entry'][0] for te in e['entries']['entry']] for e in word['def']['collins']['collins_entries']]))
            meanings = [m for m in meanings if m.get('tran')]
            for i, m in enumerate(meanings):
                m['id'] = 'sense%d' % (i + 1)
                m['tran'] = splitSense(m['tran'])[1]
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
        }

    @staticmethod
    def __get_clips(word):
        word['sents'] = [s for s in word['sents'] if s['movie']]    # pertain clips with movie downloads
        for s in word['sents']:
            s['id'] = s['_id']
            times = [(datetime.strptime(t, '%H:%M:%S.%f') - zero_time).total_seconds() for t in s['time']]
            s['start'] = max((times[0] + times[1]) / 2, times[1] - 3)
            s['end'] = min((times[2] + times[3]) / 2, times[2] + 1)
            # s['start'] = start.strftime('%H:%M:%S.%f')[:-3]
            # s['end'] = end.strftime('%H:%M:%S.%f')[:-3]
            s['length'] = s['end'] - s['start']
            s['morph'] = s['line'][s['line'].find('<em>')+4:s['line'].find('</em>')]
        return word['sents']

    @staticmethod
    def __get_movies(word):
        ids = list(set([s['movie'] for s in word['sents']]))
        d = {o['_id']: o for o in db.movies.find({'_id': {'$in': ids}, 'videofile': {'$ne': ''}})}
        for s in word['sents']:
            s['movie'] = d.get(s['movie'], {})
        for m in d.itervalues():
            assert m['videofile']
            m['id'] = ''.join([c for c in m['_id'] if c.islower() or c.isdigit()]) # convert to safe css class name
            m['rating'] = float(m['rating'])
            m['omdb']['imdbRating'] = float(m['omdb']['imdbRating'])
            m['omdb']['imdbVotes'] = int(m['omdb']['imdbVotes'].replace(',', ''))
            m['omdb']['Poster'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + m['omdb']['Poster'].split('/')[-1]
            m['poster'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + m['poster'].split('/')[-1]
        return d.values()

    @staticmethod
    def __line_length(line):
        ss = line.split()
        times = [ss[0], ss[2]]
        times = [(datetime.strptime(t, '%H:%M:%S.%f') - zero_time).total_seconds() for t in times]
        return times[1] - times[0]

    @classmethod
    def __distinct_clips(cls, clips):
        # filter context['clips'] with same videofile and 90%-similar line
        st, num = 0, len(clips)
        toremove = []
        while st < num:
            sentA = clips[st]['line'][clips[st]['line'].find('\n')+1:]
            for i in range(st):
                if clips[st]['movie']['videofile'] != clips[i]['movie']['videofile']:
                    continue
                sentB = clips[i]['line'][clips[i]['line'].find('\n')+1:]
                cover = lcs(sentA, sentB)
                ratio = 1.0 * cover / max([len(sentA), len(sentB)])
                if ratio > 0.9:
                    tmp = clips[st]
                    if cls.__line_length(tmp['line']) > cls.__line_length(clips[i]['line']):
                        tmp = clips[i]
                    toremove.append(tmp)
                else:
                    sentA = clips[st]['sent'].replace('<em>', '').replace('</em>', '')
                    sentB = clips[i]['sent'].replace('<em>', '').replace('</em>', '')
                    if sentA.strip() == sentB.strip():
                        toremove.append(clips[st])
            st += 1
        r = [c for c in clips if c not in toremove]
        if len(r) < len(clips):
            print len(clips) - len(r), 'duplicated clips removed'
        return r

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        if 'visited' not in self.request.session:
            self.request.session['visited'] = str(datetime.now())
        context['is_plugin'] = 'plugin' in self.request.GET

        word = self.request.GET.get('word') or 'default'
        r = getWordSents(word)
        context['word'] = self.__get_word(r)
        context['clips'] = self.__get_clips(r)
        context['movies'] = self.__get_movies(r)
        context['clips'] = [c for c in context['clips'] if c['movie'].get('videofile')]    # pertain clips with movie file
        context['clips'] = [c for c in context['clips'] if c['length'] < 30]    # pertain short clips
        context['clips'] = self.__distinct_clips(context['clips'])

        # sort context['clips']:
        # 1. by sense 123
        # 2. by votes
        # 3. by length of the occurence line
        # 4. by reversed clip length
        # 5. by views
        context['clips'].sort(key=lambda c: (-c['sense'], c.get('votes', 0), int(self.__line_length(c['line']) / 2), -int(c['length'] / 2), c.get('views', 0)), reverse=True)

        if context['clips']:
            clip_id = self.request.GET.get('clip_id')
            ids = [c['id'] for c in context['clips']]
            index = ids.index(clip_id) if clip_id in ids else 0
            context['active_clip'] = context['clips'][index]

        if context['movies']:
            movie_id = self.request.GET.get('movie_id', '')
            if movie_id:
                context['clips'] = [c for c in context['clips'] if c['movie']['id'] == movie_id]
            context['movies'] = [{'id': '', 'title': 'All Movies'}] + context['movies']
            ids = [m['id'] for m in context['movies']]
            context['active_movie'] = context['movies'][ids.index(movie_id)]

        if context['word']['meanings']:
            sense_id = self.request.GET.get('sense_id', '')
            if sense_id:
                context['clips'] = [c for c in context['clips'] if c['sense'] == int(sense_id[5:]) - 1]
            meanings = [{'id': '', 'tran': 'All Meanings'}] + context['word']['meanings']
            for i, m in enumerate(meanings[1:]):
                m['index'] = '%d.' % (i + 1)
            ids = [m['id'] for m in meanings]
            index = ids.index(sense_id)
            context['active_sense'] = {
                'current': meanings[index],
                'previous': meanings[index - 1],
                'next': meanings[(index + 1) % len(meanings)],
            }

        return context

    def post(self, request):
        clip_id = request.POST.get('clip_id')
        sessionid = request.POST.get('sessionid', 'unknown')
        if clip_id:
            print 'vote on %s by %s' % (clip_id, sessionid)
            clip = db.sents.find_one_and_update({'_id': clip_id}, {'$inc': {'votes': 1}}, return_document=ReturnDocument.AFTER)
            return HttpResponse(str(clip['votes']))


class AnalyticView(View):

    def get(self, request, *args, **kwargs):
        clip_id = request.GET.get('clip_id')
        clip = db.sents.find_one_and_update({'_id': clip_id}, {'$inc': {'views': 1}}, return_document=ReturnDocument.AFTER)
        return HttpResponse(str(clip['views']))
