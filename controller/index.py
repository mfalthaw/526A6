''' Controller program '''

import asyncio

from .utils import parse_args, Logger

def connect():
    ''' Connect to the IRC server '''

    # Parse arguments
    args = parse_args()

    # Setup event loop
    loop = asyncio.get_event_loop()
    coro = start(args)
    client = loop.run_until_complete(coro)

    # Run until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        Logger.debug('Keyboard interruption')

    # Close the client
    Logger.debug('Closing client')
    client.close()
    loop.run_until_complete(client.wait_closed())
    loop.close()

async def start(args):
    ''' Initialize connection to  '''
    reader, writer = await asyncio.open_connection(args.hostname, args.port)

    coro = listener(reader, writer)

    asyncio.get_event_loop().run_until_complete(coro)

    while True:
        pass


async def listener(reader, writer):
    ''' Listen for commands '''

    while True:
        commmand = input('controller is ready for commands')
        handle(command)
