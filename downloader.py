import asyncio
import os

import aiohttp
import aiofiles

import async_timeout


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

async def download_image(url, loop):
    print('start download: {}'.format(url))
    try:
        with async_timeout.timeout(5):
            async with aiohttp.ClientSession(loop=loop).get(url) as response:
                if response.status == 200:
                    content = response.content
                    file_name = url.split('/')[-1]
                    await save_file(file_name, content)
                    response.close()
                else:
                    print('Bad response for image: {}'.format(url))
                    return None
    except asyncio.TimeoutError:
        print('Cant download image: {}'.format(url))
        return None
    else:
        print('end download: {}'.format(url))
        return url

async def main(aio_loop):
    list_urls = [
        'https://cdn.photographylife.com/wp-content/uploads/2014/02/Sunset-Sunflower.jpg',
        'https://beautyty.org/wp-content/uploads/2019/01/8809240761304_1.jpg',
        'https://beautyty.org/wp-content/uploads/2019/01/8809240761304_2.jpg',
        'https://beautyty.org/wp-content/uploads/2019/01/8809240761304_3.jpg',
        'https://beautyty.org/wp-content/uploads/2019/01/8809240761304_4.jpg',
        'https://beautyty.org/wp-content/uploads/2019/01/8809240761304_44.jpg',
        'https://static.photocdn.pt/images/articles/2018/03/07/articles/2017_8/landscape_photography_lighting.jpg',
        'https://www.thesun.co.uk/wp-content/uploads/2019/07/NINTCHDBPICT000506209482.jpg'
    ]
    tasks = [aio_loop.create_task(download_image(x, aio_loop)) for x in list_urls]
    done, pending = await asyncio.wait(tasks, loop=aio_loop, return_when=asyncio.ALL_COMPLETED)

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
