# from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View

import json
from gensim.models.word2vec import Word2Vec
from .settings import MODEL_FILE

class MyView(View):

    model = Word2Vec.load_word2vec_format(MODEL_FILE, binary=True)

    @classmethod
    def n_similarity(cls, s1, s2):
        # TODO: preprocesses of s1, s2 goes here
        s1, s2 = cls.__removeStopwords(s1), cls.__removeStopwords(s2)
        if not s1 or not s2:
            return 0.0
        return cls.model.n_similarity(s1, s2)

    @classmethod
    def __removeStopwords(cls, tokens):
        withoutstops = []
        for word in tokens:
            if not word or (word not in cls.model):
                continue
            withoutstops.append(word)
        return withoutstops

    @classmethod
    def get(cls, request, *args, **kwargs):
        s1, s2 = request.GET.get('s1', '[]'), request.GET.get('s2', '[]')
        s1, s2 = json.loads(s1), json.loads(s2)
        return JsonResponse({'n_similarity': cls.n_similarity(s1, s2)})

# l1, l2 = ['this', 'is'], ['good']
# r = requests.get('http://166.111.139.15:8003/gensim/', {'s1': json.dumps(l1), 's2': json.dumps(l2)}).json()
# print r['n_similarity']
