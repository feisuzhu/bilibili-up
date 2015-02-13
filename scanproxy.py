from gevent import monkey
monkey.patch_all()

# -- stdlib --
import argparse

# -- third party --
from gevent.pool import Pool
import gevent
import requests

# -- own --

# -- code --
parser = argparse.ArgumentParser('scanproxy')
parser.add_argument('proxylist')
parser.add_argument('output')
options = parser.parse_args()

good = open(options.output, 'w')
lst = open(options.proxylist).read().split()


def check(addr):
    with gevent.Timeout(30):
        resp = requests.get('http://www.baidu.com/robots.txt', proxies={'http': 'http://' + addr})
        if 'yisouspider' in resp.content:
            print 'GOOD CONNECT', addr
            # good.write(addr + ' CONNECT\n')
            good.write(addr + '\n')
            return

        # resp = requests.get('http://%s/robots.txt' % addr, headers={'Host': 'www.baidu.com'})
        # if 'yisouspider' in resp.content:
        #     print 'GOOD TRANSPARENT', addr
        #     good.write(addr + ' TRANSPARENT\n')
        #     return
        print 'BAD', addr


pool = Pool(20)
for i in lst:
    pool.spawn(check, i)

pool.join()
