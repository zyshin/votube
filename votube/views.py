from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView

import json
from itertools import chain
from datetime import datetime
from SubWSD.subWSD import getWordSents
from SubWSD.classifySense import splitSense

from pymongo import MongoClient, ReturnDocument
db = MongoClient('166.111.139.42').dev
db.authenticate('test', 'test')


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
            for m in meanings:
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
            # 'forms': forms,
            'meanings': meanings,
        }

    @staticmethod
    def __get_clips(word):
        word['sents'] = [s for s in word['sents'] if s['movie']]
        zero_time = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')
        for s in word['sents']:
            s['id'] = s['_id']
            times = [(datetime.strptime(t, '%H:%M:%S.%f') - zero_time).total_seconds() for t in s['time']]
            s['start'] = max((times[0] + times[1]) / 2, times[1] - 3)
            s['end'] = min((times[2] + times[3]) / 2, times[2] + 1)
            # s['start'] = start.strftime('%H:%M:%S.%f')[:-3]
            # s['end'] = end.strftime('%H:%M:%S.%f')[:-3]
            s['length'] = s['end'] - s['start']
        return word['sents']

    @staticmethod
    def __get_movies(word):
        ids = list(set([s['movie'] for s in word['sents']]))
        d = {o['_id']: o for o in db.movies.find({'_id': {'$in': ids}})}
        for s in word['sents']:
            s['movie'] = d.get(s['movie'], {})
        for m in d.itervalues():
            m['rating'] = float(m['rating'])
            m['omdb']['imdbRating'] = float(m['omdb']['imdbRating'])
            m['omdb']['imdbVotes'] = int(m['omdb']['imdbVotes'].replace(',', ''))
            m['omdb']['Poster'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + m['omdb']['Poster'].split('/')[-1]
            m['poster'] = 'http://pi.cs.tsinghua.edu.cn/lab/moviedict/movies/poster/' + m['poster'].split('/')[-1]
        return d.values()

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        word = self.request.GET.get('word') or 'default'
        r = getWordSents(word)
        context['is_plugin'] = 'plugin' in self.request.GET
        context['word'] = self.__get_word(r)
        context['clips'] = self.__get_clips(r)
        context['movies'] = self.__get_movies(r)
        
        from random import shuffle
        shuffle(context['clips'])
        # TODO: sort and filter context['clips']

        if context['clips']:
            clip_id = self.request.GET.get('clip_id')
            ids = [c['id'] for c in context['clips']]
            index = ids.index(clip_id) if clip_id in ids else 0
            context['active_clip'] = context['clips'][index]

        return context

    def post(self, request):
        clip_id = request.POST.get('clip_id')
        clip = db.sents.find_one_and_update({'_id': clip_id}, {'$inc': {'votes': 1}}, return_document=ReturnDocument.AFTER)
        return HttpResponse(str(clip['votes']))
