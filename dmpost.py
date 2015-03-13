# -*- coding: utf-8 -*-
import gevent
from gevent import monkey
monkey.patch_all()

# -- stdlib --
from argparse import ArgumentParser
import json
import os
import random
import re
import sys
import time

# -- third party --
import arrow
import requests

# -- own --

# -- code --
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parser = ArgumentParser('dmpost')
parser.add_argument('aid', type=int)
parser.add_argument('pid', type=int)
parser.add_argument('dmpool', type=str)
parser.add_argument('cookies', type=str)
parser.add_argument('proxies', type=str)
parser.add_argument('--video-length', type=int, default=300)
parser.add_argument('--post-interval', type=int, default=60)
options = parser.parse_args()

dmpool = [i.strip() for i in open(options.dmpool).read().decode('utf-8').split('\n')]
cookies = [json.loads(i) for i in open(options.cookies).read().split('\n') if i]
proxies = [i.strip() for i in open(options.proxies).read().split('\n') if i]

sessions = None


def build_sessions():
    global sessions
    sessions = []

    for c, p in zip(cookies, proxies):
        s = requests.session()
        s.cookies.update(c)
        s.proxies.update({'http': 'http://' + p})
        s.headers.update({
            'Origin': 'https://secure.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36 SE 2.X MetaSr 1.0',
            'X-Requested-With': 'ShockwaveFlash/13.0.0.206',
        })
        sessions.append(s)

    random.shuffle(sessions)

build_sessions()

video_url = 'http://www.bilibili.com/video/av%s/index_%s.html' % (options.aid, options.pid)

while True:
    t = arrow.now()
    dm = random.choice(dmpool)[:16] + 'poi'

    sessions or build_sessions()

    print "[%s av%d] %s" % (t.format('HH:mm:ss'), options.aid, dm),

    try:
        with gevent.Timeout(15):
            session = sessions.pop(0)
            page = session.get(video_url)
            cid = int(re.findall(r'cid=([0-9]+)&aid=%s' % options.aid, page.content)[0])

            url = 'http://interface.bilibili.com/dmpost?cid=%s&aid=%s&pid=%s' % (cid, options.aid, options.pid)

            rst = session.post(url, data={
                'fontsize': 25,
                'color': random.randrange(0, 16777216),
                'cid': cid,
                'message': dm,
                'date': t.format('YYYY-MM-DD HH:mm:ss'),
                'playTime': random.random() * options.video_length,
                'mode': 1,
                'pool': 0,
                'rnd': random.randint(3847299, 777766627334),
            })
            if not rst.ok:
                print 'Fail'
                continue

            print 'Done'
            sessions.append(session)

    except (Exception, gevent.Timeout):
        import traceback
        traceback.print_exc()
        gevent.sleep(0.1)
        continue

    time.sleep(options.post_interval)
