# -*- coding: utf-8 -*-

# -- stdlib --
from argparse import ArgumentParser
import json
import os
import re
import sys

# -- third party --
import requests

# -- own --

"http://member.bilibili.com/video_manage.html?act=dmm&dm_inid=3030522"
# -- code --
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parser = ArgumentParser('dmpost')
parser.add_argument('dm_inid', type=int)
parser.add_argument('pool', type=int)
parser.add_argument('cookie', type=str)
parser.add_argument('keyword', type=str)
options = parser.parse_args()

cookie = json.loads(open(options.cookie).read())

session = requests.session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36 SE 2.X MetaSr 1.0',
})
session.cookies.update(cookie)

print 'Fetching danmaku...'

# {"dmid":"770936538","f":"0","p":"17.034","m":"\u89c1\u4e1c\u65b9\u6eda\u8fdb\u6765","t":"1423144673","mo":"1","cl":"ffffff","fs":"25"}

resp = session.get("http://member.bilibili.com/video_manage.html", params={'act': 'dmm', 'dm_inid': options.dm_inid})
danmaku, = re.findall(r'^var member_dmm_dmlist=(.+);', resp.text, re.MULTILINE)
danmaku = json.loads(danmaku)
lst = [i['dmid'] for i in danmaku if options.keyword in i['m']]

print 'Removing %d danmakus...' % len(lst)
session.post(
    'http://member.bilibili.com/video_manage.do',
    params={'act': 'dmm', 'output': 'json'},
    data={
        'dm_inid': options.dm_inid, 'pool': options.pool,
        'reportToAdmin': '', 'mode': 'del',
        'seldm[]': lst, 'sid': cookie['sid']
    },
)

print 'Done'
