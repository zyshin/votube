import requests, json
# import requests_cache

USE_LOCAL_MODEL = False
if USE_LOCAL_MODEL:
    from myapp.views import MyView

class gensimModel:

    def n_similarity(self, s1, s2):
        if USE_LOCAL_MODEL:
            return MyView.n_similarity(s1, s2)
        r = requests.get('http://166.111.139.15:8003/gensim/',
            {'s1': json.dumps(s1), 's2': json.dumps(s2)})
        r = r.json()
        return r['n_similarity']

#     def hasword(self, word):
#         r = requests.get('http://166.111.139.15:8003/gensim/',
#             {'word': word})
#         r = r.json()
#         return r['hasword']

# model = gensimModel()
# l1, l2 = ['this', 'is'], ['good', 'boy']
# print model.n_similarity(l1, l2)
# print model.hasword('hello')
# print model.hasword('?')

