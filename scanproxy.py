from gevent import monkey
monkey.patch_all()

# -- stdlib --
import argparse
import time

# -- third party --
from gevent.pool import Pool
import gevent
import requests

# -- own --

# -- code --
parser = argparse.ArgumentParser('scanproxy')
parser.add_argument('proxylist')
parser.add_argument('output')
parser.add_argument('--url', default='http://www.baidu.com/robots.txt')
parser.add_argument('--keyword', default='yisouspider')
parser.add_argument('--content', action='store_true')
options = parser.parse_args()

good = open(options.output, 'w')
lst = open(options.proxylist).read().split()


def check(addr):
    with gevent.Timeout(15):
        t = time.time()
        resp = requests.get(options.url, proxies={'http': 'http://' + addr, 'https': 'http://' + addr})
        if options.keyword in resp.content:
            print 'GOOD CONNECT', int((time.time() - t) * 100000) / 100.0, addr
            # good.write(addr + ' CONNECT\n')
            good.write(addr + '\n')

            if options.content:
                print resp.content

            return

        # resp = requests.get('http://%s/robots.txt' % addr, headers={'Host': 'www.baidu.com'})
        # if 'yisouspider' in resp.content:
        #     print 'GOOD TRANSPARENT', addr
        #     good.write(addr + ' TRANSPARENT\n')
        #     return
        print 'BAD', addr
        if options.content:
            print resp.content


pool = Pool(30)
for i in lst:
    pool.spawn(check, i)

pool.join()
