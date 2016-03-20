# coding=utf-8
import requests
# import requests_cache
# import six.moves.cPickle as pickle

# requests_cache.install_cache("parse_cache")


class Tagger:
    # filename = "tagged.pk"
    # CACHE = {}

    # def __init__(self, filename="tagged.pk"):
    #     self.filename = filename
    #     try:
    #         with open(filename, 'rb') as a:
    #             self.CACHE = pickle.load(a)
    #     except Exception, e:
    #         self.CACHE = {}
    #     self.savecnt = 0

    # def __del__(self):
    #     with open(self.filename, 'wb') as f:
    #         pickle.dump(self.CACHE, f)

    def parse(self, s):
        r = requests.post(
            'http://166.111.139.15:9000/?properties%3d%7b%22annotators%22%3a%22tokenize%2cssplit%2cpos%2clemma%22%2c%22outputFormat%22%3a%22json%22%7d%0a', data=s)
        return r.json()

    def tag(self, sent):
        # sent = sent.lower()
        # print sent
        parsed = self.parse(sent)
        sentences = parsed['sentences']
        tokens = []
        for sentence in sentences:
            tokens += sentence['tokens']
        return tokens


# tagger = Tagger()
# print tagger.tag("I <i>like</i> you and he <i>likes</i> me.")
# print "hello hi".find('e')
