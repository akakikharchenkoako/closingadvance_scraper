#!/usr/bin/env python
print('If you get error "ImportError: No module named \'six\'"'+\
    'install six:\n$ sudo pip install six');
import sys
if sys.version_info[0]==2:
    import six
    from six.moves.urllib import request
    opener = request.build_opener(
        request.ProxyHandler(
            {'http': 'http://127.0.0.1:24002'}))
    print(opener.open('http://lumtest.com/myip.json').read())
if sys.version_info[0]==3:
    import urllib.request
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {'http': 'http://127.0.0.1:24002'}))
    print(opener.open('https://www.realtor.com/').read())
