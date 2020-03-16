import asyncio
import os

import aiohttp
import aiofiles

import async_timeout
import pika


async def save_file(file_name, data):
    async with aiofiles.open(file_name, 'wb') as f:
        i = 0
        while True:
            chunk = await data.read(1024)
            if not chunk:
                await f.flush()
                print('saved: {}'.format(file_name))
                return os.path.abspath(file_name)
            i += 1
            print('{}: chunk {}'.format(file_name, i))
            await f.write(chunk)

async def download_image(url, loop, messages_part):
    print('start download: {}'.format(url))
    try:
        with async_timeout.timeout(5):
            async with aiohttp.ClientSession(loop=loop).get(url) as response:
                if response.status == 200:
                    content = response.content
                    file_name = '{}-'.format(messages_part) + url.split('/')[-1]
                    await save_file(file_name, content)
                    response.close()
                else:
                    print('Bad response for image: {}'.format(url))
                    return None
    except asyncio.TimeoutError:
        print('Cant download image: {}'.format(url))
        return None
    except Exception as e:
        print('Error while download')
    else:
        print('end download: {}'.format(url))
        return url


async def main(aio_loop):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
    channel = connection.channel()
    channel.queue_declare(queue='download_stream', durable=True)
    channel.basic_qos(prefetch_count=1)

    list_urls = []
    n = 0
    while True:
        method_frame, header_frame, body = channel.basic_get(queue='download_stream')
        if not method_frame:
            continue
        elif method_frame.NAME == 'Basic.GetEmpty':
            pass
        else:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            list_urls.append('{}'.format(body.decode("utf-8")))

        if len(list_urls) >= 5:
            n += 1
            tasks = [aio_loop.create_task(download_image(url, aio_loop, n)) for url in list_urls]
            done, pending = await asyncio.wait(tasks, loop=aio_loop, return_when=asyncio.ALL_COMPLETED)

            list_urls = []

            for future in pending:
                print('future was canceled')
                future.cancel()

            for future in done:
                print('future was done')
                try:
                    print('result: {}'.format(future.result()))
                except Exception as e:
                    print('future was broken')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
