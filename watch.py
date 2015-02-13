import requests
import random
import sys

resp = requests.get('http://www.bilibili.com/index/ding.json?rnd=' + str(random.random()), timeout=1)
rst = resp.json()[sys.argv[1]]
rst = [i[1]['title'] for i in sorted(rst.items())]
kw = sys.argv[2].decode('utf-8')
for i in rst:
    if kw in i:
        print '>>>>>', i.encode('utf-8'), '<<<<<'
    else:
        print i.encode('utf-8')
