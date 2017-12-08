''' Controller program '''

import asyncio

from .utils import parse_args, Logger
from .protocol import Messenger, handshake
from .handlers import Handler
from .errors import QuitSignal

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
    try:
        messenger = await Messenger.create(args.channel, args.hostname, args.port, args.secret_phrase)
    except QuitSignal:
        Logger.log('Failed to connect to server, timed out')

    handler = Handler(messenger)

    # Handshake
    await handshake(messenger)

    # Setup the handler (leave room for other misc tasks)
    tasks = [
        handler.handle(),
    ]

    # Combine the tasks
    client = asyncio.gather(*tasks)

    # Wait on both tasks
    await client
