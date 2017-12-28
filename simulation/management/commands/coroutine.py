from django.core.management.base import BaseCommand, CommandError
import asyncio
import urllib


class Command(BaseCommand):
    help = '基于协程的多任务异步非阻塞并发运行~~'
    current = 0
    host = 'lusion-blog.cn'

    def handle(self, *args, **options):
        try:
            print(self.help)

            # 定义开启并发协程数
            nums = 50
            coroutines = []
            for i in range(nums):
                coroutines.append(i)

            loop = asyncio.get_event_loop()
            tasks = [self.wget(coroutine_index) for coroutine_index in coroutines]
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()

        except ImportError:
            raise CommandError('error')

    def formatHeader(self, url, method='GET', data={}):

        # 获取host
        protocol, s1 = urllib.parse.splittype(url)
        host, s2 = urllib.parse.splithost(s1)
        # 封装数据
        if method == 'GET':
            header = 'GET %s HTTP/1.0\r\nHost: %s\r\n\r\n' % (url, host)
        elif method == 'POST':
            # 序列化application/x-www-form-urlencoded对应的字符串
            postStr = urllib.parse.urlencode(data)

            # 拼装字符串
            header = 'POST %s HTTP/1.0\r\n' \
                     'cache-control: no-cache\r\n' \
                     'Content-Type: application/x-www-form-urlencoded\r\n' \
                     'Accept: */*\r\n' \
                     'Host: %s\r\n' \
                     'accept-encoding: gzip, deflate\r\n' \
                     'content-length: %d\r\n' \
                     'Connection: keep-alive\r\n' \
                     '\r\n' \
                     '%s' % (url, host, len(postStr), postStr)
        return header

    # 开始抓包
    async def wget(self, coroutine_index):

        # 执行总任务数
        while self.current < 300:

            # 当前执行请求任务数量
            self.current += 1

            host = self.host
            url = 'http://%s/home/index/search?term=flume&coroutine=' % host + str(coroutine_index)
            # 发送GET请求封装
            # header = self.formatHeader(url)
            # 发送POST请求封装
            postData = {
                'params_1': 'hello',
                'params_2': 'world',
            }
            header = self.formatHeader(url, 'POST', postData)

            connect = asyncio.open_connection(host, 80)
            reader, writer = await connect
            writer.write(header.encode('utf-8'))
            await writer.drain()
            blocks = []
            while True:
                line = await reader.readline()
                # line = await reader.read()
                # if line == b'\r\n':
                if not line:
                    break
                blocks.append(line)
            data = b''.join(blocks)
            print('==========开始返回响应=========')
            print(data.decode())
            print('==========返回响应结束=========')
            writer.close()
