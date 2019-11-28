import asyncio
import aiohttp
import time
import sys
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError
from proxypool.db import RedisClient
from proxypool.setting import *


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
    
    async def test_single_proxy(self, proxy):
        """
        测试单个代理
        :param proxy:
        :return:
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                # real_proxy = 'https://' + proxy
                print('正在测试', proxy)
                async with session.get(url=TEST_URL, proxy=real_proxy, headers=self.headers, timeout=15, allow_redirects=False) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法 ', response.status, 'IP', proxy)
            except (ClientError, aiohttp.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)
    
    def run(self):
        """
        测试主函数
        :return:
        """
        print('测试器开始运行')
        count = self.redis.count()
        print('当前剩余', count, '个代理')
        # 每次运行本测试单元，应该先将库存里满分的代理取出来测试，剔除无效代理，保证开启线程池后提供的代理即是可用的；
        useful_ip = self.redis.all_useful()
        if useful_ip:
            count_usefully = len(useful_ip)
            print('第一个有用的代理: {}'.format(useful_ip[0]), '共{}个'.format(count_usefully))
            for i in range(0, count_usefully, BATCH_TEST_SIZE):
                start = i
                stop = min(i + BATCH_TEST_SIZE, count_usefully)
                print('正在测试第', start + 1, '-', stop, '个代理(usefully)')
                self.batch_proxies(useful_ip[start: stop + 1])
        else:
            print('当前无可用代理，请等待...')
        for i in range(0, count, BATCH_TEST_SIZE):
            start = i
            stop = min(i + BATCH_TEST_SIZE, count)
            print('正在测试第', start + 1, '-', stop, '个代理(normally)')
            test_proxies = self.redis.batch(start, stop)
            self.batch_proxies(test_proxies)

    def batch_proxies(self, test_proxies):
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
            sys.stdout.flush()
            time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)
