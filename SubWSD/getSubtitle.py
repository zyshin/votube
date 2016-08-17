# coding=utf-8

import json
import requests
import re
# import requests_cache

# requests_cache.install_cache("subtitle_cache")


def isLineStart(sent):
    ch, sent = splitSent(sent)
    return ((sent and sent[0].isupper()) or sent.startswith('\"'))


def isLineEnd(line):
    ch, line = splitSent(line)
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

def splitSent(sent):
    ss = sent.split('\r\n') if '\r\n' in sent else sent.split('\n')
    s1 = ss[0] if len(ss) > 0 else ''
    s2 = ss[1] if len(ss) > 1 else ''
    n1 = sum([1 for c in s1 if re.match(r'[a-zA-Z ]', c)])
    n2 = sum([1 for c in s2 if re.match(r'[a-zA-Z ]', c)])
    r = (s2, s1) if n1 > n2 else (s1, s2)   # (ch, en)
    return r

def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring

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
    while start > 0 and \
            not isLineStart(splitTime(title[start])[1].strip()) and \
            not isLineEnd(splitTime(title[start-1])[1].strip()):
        start -= 1
    while end < length - 1 and \
            not isLineEnd(splitTime(title[end])[1].strip()) and \
            not isLineStart(splitTime(title[end+1])[1].strip()):
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
    fullsent, fullsent_ch = "", ""
    for i in range(start, end + 1):
        if i == ans['line_no']:
            ch, en = splitSent(splitTime(match)[1].strip())
        else:
            ch, en = splitSent(splitTime(title[i])[1].strip())
        fullsent = combineSents(fullsent, en)
        fullsent_ch = combineSents(fullsent_ch, ch)
    # ans['sent'] = strQ2B(fullsent)
    ans['sent'] = fullsent
    ans['sent_ch'] = fullsent_ch
    return ans


def getSubtitles(word):
    left = "http://166.111.139.15:8983/solr/techproducts/select?q=title%3A"
    right = "+AND+lang%3A中英&rows=10000&wt=json&indent=true&hl=true&hl.fl=title&hl.snippets=10&hl.fragsize=0&hl.maxAnalyzedChars=1048576"
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
