''' handle '''

import asyncio

from .quit import quit_handle
from ..utils import Logger, AsyncInput
from ..errors import QuitSignal

class Handler:
    ''' Handle the different commands '''

    __BASIC_COMMANDS = [
        'attack',
        'move',
        'shutdown',
        'status',
    ]

    __HANDLERS = {
        'quit': quit_handle,
    }

    def __init__(self, messenger):
        self.messenger = messenger

    async def handle(self):
        ''' Deal with the command appropriately '''

        while True:

            # listen for user input OR for heartbeat
            done, pending = await asyncio.wait([
                self.messenger.listen_irc(),
                self.__listen_user()
            ], return_when=asyncio.FIRST_COMPLETED)

            # Completed is always listen_user(), cancel pending
            pending.cancel()
            await pending

            # Deal with results
            line = done.pop().result()

            # Parse line
            split_line = line.split(' ', num=1)
            command = split_line[0]

            # If basic command, forward message to IRC
            if command in Handler.__BASIC_COMMANDS:
                self.messenger.send_channel(line)

            # If advanced command, handle
            try:
                await Handler.__HANDLERS[command](self.messenger)

            # Otherwise, inform user their command was incorrect
            except KeyError:
                Logger.log('invalid command: {}\n'.format(command))

            except QuitSignal:
                Logger.log('quitting...')
                await self.messenger.close()
                await asyncio.get_event_loop().stop()
                return

    async def __listen_user(self):
        ''' Listen for input from user '''
        ainput = AsyncInput()
        return await ainput.read('awaiting command...')
