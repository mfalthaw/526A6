''' protocol messenger '''

import re

from .heartbeat import heartbeat

class Messenger:
    ''' Handle messages between IRC server and client '''

    __PING_REGEX = re.compile(r'')

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
            if Messenger.__PING_REGEX.match(msg):
                await heartbeat(self, msg)
                continue

            return msg

    async def heartbeat(self):
        ''' '''
        pass
