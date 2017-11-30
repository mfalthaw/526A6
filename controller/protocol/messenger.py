''' protocol messenger '''

import re

from .heartbeat import heartbeat, is_heartbeat

class Messenger:
    ''' Handle messages between IRC server and client '''

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, msg):
        ''' send message to IRC server '''
        return await self.writer.write('{0}\r\n'.format(msg))

    async def read(self):
        ''' Wait for a message from the IRC server '''
        while True:
            msg = await self.reader.readline().strip()
            if is_heartbeat(msg):
                await heartbeat(self, msg)
                continue

            return msg

    async def listen_heartbeat(self):
        ''' Listen for heartbeat, raise error if not heartbeat message '''
        while True:
            msg = await self.reader.readline().strip():
            if is_heartbeat(msg):
                await heartbeat(self, msg)
            else:
                raise Error('invalid heartbeat message: {0}'.format(msg))
