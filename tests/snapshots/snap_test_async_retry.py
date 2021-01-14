# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_async_retry 1'] = '''(
    <ClientResponse(https://httpbin.org/get) [200 OK]>
<CIMultiDictProxy('Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Origin': '*', 'Connection': 'keep-alive', 'Content-Length': '310', 'Content-Type': 'application/json', 'Date': 'Tue, 15 Dec 2020 20:55:02 GMT', 'Server': 'gunicorn/19.9.0')>
,
    200,
    <CIMultiDictProxy('Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Origin': '*', 'Connection': 'keep-alive', 'Content-Length': '310', 'Content-Type': 'application/json', 'Date': 'Tue, 15 Dec 2020 20:55:02 GMT', 'Server': 'gunicorn/19.9.0')>
)'''

snapshots['test_async_retry 2'] = '''{
    'args': {
    },
    'headers': {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'httpbin.org',
        'User-Agent': 'Python/3.7 aiohttp/3.7.3',
        'X-Amzn-Trace-Id': 'Root=1-5fd922a6-21bda3482642f6bb6baa9670'
    },
    'origin': '147.236.152.14',
    'url': 'https://httpbin.org/get'
}'''
