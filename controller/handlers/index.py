''' handle '''

import asyncio

from .quit import quit_handle
from .attack import attack_handle
from .move import move_handle
from .shutdown import shutdown_handle
from .status import status_handle
from .lmove import lmove_handle
from .list import list_handle

from ..utils import Logger, AsyncInput
from ..errors import QuitSignal

class Handler:
    ''' Handle the different commands '''

    __HANDLERS = {
        'quit': quit_handle,
        'attack': attack_handle,
        'move': move_handle,
        'shutdown': shutdown_handle,
        'status': status_handle,
        'lmove': lmove_handle,
        'list': list_handle,
    }

    def __init__(self, messenger):
        self.messenger = messenger

    async def handle(self):
        ''' Deal with the command appropriately '''

        while True:

            # listen for user input OR for message from server
            done, pending = await asyncio.wait(
                [self.messenger.listen_irc(), self.__listen_user()],
                return_when=asyncio.FIRST_COMPLETED)

            # Reauthenticate
            self.messenger.authenticate()

            # Completed is always listen_user(), cancel pending
            for task in pending:
                task.cancel()

            # Deal with results
            line = done.pop().result()

            # Parse line
            split_line = line.split(' ', 1)
            command = split_line[0]

            # Handle commands
            try:
                await Handler.__HANDLERS[command](self.messenger, line)

            # Otherwise, inform user their command was incorrect
            except KeyError:
                Logger.log('invalid command: {}\n'.format(command))

            except QuitSignal:
                Logger.log('quitting...')
                self.messenger.close()
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                return

            except SystemExit:
                pass

    async def __listen_user(self):
        ''' Listen for input from user '''
        ainput = AsyncInput()
        return await ainput.read('awaiting command...')
