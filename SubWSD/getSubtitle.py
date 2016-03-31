# coding=utf-8

import json
import requests
# import requests_cache

# requests_cache.install_cache("subtitle_cache")


def isLineStart(sent):
    return (sent[0].isupper() or sent.startswith('\"'))


def isLineEnd(line):
    return (line.endswith('.') or line.endswith('?') or line.endswith('!') or line.endswith('\"')) and not line.endswith('...')


def combineSents(before, after):
    if before.endswith('...'):
        before = before[:-3]
    if after.startswith('...'):
        after = after[3:]
    return (before.strip() + ' ' + after.strip()).strip()


def splitTime(line):
    tmp = line.split('\r\n')
    if len(tmp) == 1:
        tmp = line.split('\n')
    time = tmp[0]
    sent = line.replace(time, '')
    return [time, sent]


def findFull(match, title):
    ans = {}
    match = match.strip()
    time = splitTime(match)[0]
    # print match
    length = len(title)
    for i in range(length):
        if title[i].startswith(time):
            ans['line_no'] = i
    start = ans['line_no']
    end = ans['line_no']
    while (not isLineStart(splitTime(title[start])[1].strip())) and start > 0:
        start -= 1
    while (not isLineEnd(splitTime(title[end])[1].strip())) and end < length - 1:
        end += 1

    starttime = splitTime(title[start])[0].split('-->')[0].strip()
    endtime = splitTime(title[end])[0].split('-->')[1].strip()
    if start > 0:
        beforetime = splitTime(title[start - 1])[0].split('-->')[1].strip()
    else:
        beforetime = starttime
    if end < length - 1:
        aftertime = splitTime(title[end + 1])[0].split('-->')[0].strip()
    else:
        aftertime = endtime
    time = [beforetime, starttime, endtime, aftertime]
    ans['time'] = time
    fullsent = ""
    for i in range(start, end + 1):
        if i == ans['line_no']:
            fullsent = combineSents(fullsent, splitTime(match)[1])
        else:
            fullsent = combineSents(fullsent, splitTime(title[i])[1])
    ans['sent'] = fullsent
    # print ans
    # print fullsent
    return ans


def getSubtitles(word):
    left = "http://166.111.139.15:8983/solr/techproducts/select?q=title%3A"
    right = "+AND+lang%3A英文&rows=10000&wt=json&indent=true&hl=true&hl.fl=title&hl.snippets=10&hl.fragsize=0&hl.maxAnalyzedChars=1048576"
    url = left + word.encode('utf-8') + right
    url = url.replace(' ', "%20")
    response = requests.get(url).json()
    highlighting = response["highlighting"]
    docs = response['response']['docs']

    ans = []
    for doc in docs:
        # print doc['id']
        matched = highlighting[doc['id']]['title']
        for match in matched:
            full = findFull(match, doc['title'])
            full['subtitle'] = doc['id']
            full['line'] = match
            # print full
            ans.append(full)
    # print len(ans)
    return ans

# getSubtitles("strike")
# print "...like."[3:]
