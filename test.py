import asyncio

def test():
    loop = asyncio.get_event_loop()
    tasks = [
        a(),
        b()
    ]

    client = asyncio.gather(*tasks)

    try:
        loop.run_until_complete(client)
    except KeyboardInterrupt:
        print('closing')

    client.cancel()


async def a():
    while True:
        print('a')
        await asyncio.sleep(5)

async def b():
    while True:
        print('b')
        await asyncio.sleep(1)

test()
