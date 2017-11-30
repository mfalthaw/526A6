import asyncio

def test():
    loop = asyncio.get_event_loop()
    coro = main()

    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt:
        print('\n...closing')

    coro.close()
    asyncio.wait(coro)


async def main():
    tasks = [
        a(),
        b()
    ]

    client = asyncio.gather(*tasks)
    await client


async def a():
    while True:
        print('a')
        await asyncio.sleep(5)

async def b():
    while True:
        print('b')
        await asyncio.sleep(1)

test()
