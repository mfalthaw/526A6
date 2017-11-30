''' handle '''

import asyncio

from .attack import attack_handle
from .move import move_handle
from .quit import quit_handle
from .shutdown import shutdown_handle
from .status import status_handle

class Handler:

    __HANDLERS = {
        'attack' = attack_handle,
        'move' = move_handle,
        'quit' = quit_handle,
        'shutdown' = shutdown_handle,
        'status' = status_handle,
    }

    __init__(self, messenger):
        self.messenger = messenger


    async def listen():
        ''' Listen for commands from the user or IRC server '''
        pass

    async def handle(command):
        ''' Deal with the command appropriately '''

        # listen for user input OR for heartbeat
        done, pending = await asyncio.wait([
            self.__listen_heartbeat(),
            self.__listen_user()
        ], return_when=asyncio.FIRST_COMPLETED)

    async def __listen_heartbeat(self):
        ''' listen for heartbeat from server '''
        return await self.messenger.listen_heartbeat()

    async def __listen_user(self):
        ''' Listen for input from user '''
        raise NotImplemented()
