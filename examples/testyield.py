


def averager():
     total = 0.0
     count = 0
     average= ''
     while True:
        term = yield average
        total += term
        count += 1
        average = total/count


# coro_avg = averager()
# next(coro_avg)

def consumer():
    r = ''
    while True:
        n = yield r
        # if not n:
        #     return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    # c.send(None)
    next(c)
    print('')
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()
#
# c = consumer()
# produce(c)

import asyncio
import time
import scrapy

async def job(t):
    print('Start job', t)
    await asyncio.sleep(t)
    print('Job', t, 'takes', t, 'S')

async def main(loop):
    tasks = [
        asyncio.create_task(job(t)) for t in range(1, 3)
        # loop.create_task(job(t)) for t in range(1, 3)     # loop 和 asyncio 都可以
    ]
    # task2 = asyncio.create_task()     # create出来的task要么赋值给变量 要么添加 await ？ 是这样吗？
    # await asyncio.ensure_future()
    await asyncio.wait(tasks)           # tasks如果是单个任务，倒是没见用wait（）， tasks为list时，一定有.wait()

t1 = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
print('Async total time:', time.time()-t1)
