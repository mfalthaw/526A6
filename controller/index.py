''' Controller program '''

import asyncio

from .utils import parse_args, Logger
from .protocol import Messenger, handshake
from .handlers import Handler

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
    except ConnectionRefusedError:
        Logger.log('No such IRC server')

    # Close the client
    Logger.debug('Closing client')
    coro.close()
    loop.close()
    return

async def connect(args):
    ''' Connect to IRC server and start tasks '''
    reader, writer = await asyncio.open_connection(args.hostname, port=args.port, loop=asyncio.get_event_loop())
    messenger = Messenger(reader, writer, args.channel)
    handler = Handler(messenger)

    # Handshake
    await handshake(messenger, args.secret_phrase)

    # Setup the handler (leave room for other misc tasks)
    tasks = [
        handler.handle(),
    ]

    # Combine the tasks
    client = asyncio.gather(*tasks)

    # Wait on both tasks
    await client
