''' Controller program '''

import asyncio

from .utils import parse_args, Logger
from .protocol import heartbeat
from .handlers import handle

def start():
    ''' Setup event loop and start controller '''

    # Parse arguments
    args = parse_args()

    # Setup event loop
    loop = asyncio.get_event_loop()
    coro = connect(args)


    # Run until Ctrl+C is pressed
    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt:
        Logger.debug('Keyboard interruption')

    # Close the client
    Logger.debug('Closing client')
    coro.close()
    loop.run_until_complete(coro)
    loop.close()

async def connect(args):
    ''' Connect to IRC server and start tasks  '''
    reader, writer = await asyncio.open_connection(args.hostname, args.port)

    # Handshake

    # Setup the handler and heartbeat
    tasks = [
        handle(reader, writer),
        heartbeat(reader, writer)
    ]

    # Combine the tasks
    client = asyncio.gather(*tasks)

    # Wait on both tasks
    await client
