''' handle '''

import asyncio

from .quit import quit_handle
from ..utils import Logger

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


    async def listen(self):
        ''' Listen for commands from the user or IRC server '''
        pass

    async def handle(self):
        ''' Deal with the command appropriately '''

        while True:

            # listen for user input OR for heartbeat
            done, pending = await asyncio.wait([
                self.__listen_heartbeat(),
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

            # If basic command, forward message to
            if command in Handler.__BASIC_COMMANDS:
                self.messenger.send_channel(line)

            try:
                # If advanced command, handle
                Handler.__HANDLERS[command](self.messenger)
            except KeyError:
                # Otherwise, inform user their command was incorrect
                Logger.log('invalid command')



    async def __listen_heartbeat(self):
        ''' listen for heartbeat from server '''
        return await self.messenger.listen_heartbeat()

    async def __listen_user(self):
        ''' Listen for input from user '''
        raise NotImplementedError()
