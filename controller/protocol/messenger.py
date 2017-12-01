''' protocol messenger '''

import re

from .heartbeat import heartbeat, is_heartbeat
from ..utils import Logger

class Messenger:
    ''' Handle messages between IRC server and client '''

    def __init__(self, reader, writer, channel):
        self.reader = reader
        self.writer = writer
        self.channel = channel

    async def send(self, msg):
        ''' send message to IRC server '''
        return await self.writer.write('{0}\r\n'.format(msg))

    async def send_channel(self, msg):
        ''' send a private message to channel '''
        return await self.writer.write('PRIVMSG {0} :{1}\r\n'.format(msg, self.channel))

    async def join(self):
        ''' Join the channel '''
        return await self.writer.write('JOIN :{}'.format(self.channel))

    async def send_quit(self):
        ''' Send quit message '''
        return await self.writer.write('QUIT')

    async def read(self):
        ''' Wait for a message from the IRC server '''
        while True:
            msg = await self.reader.readline().strip()
            if is_heartbeat(msg):
                await heartbeat(self, msg)
                continue

            return msg

    async def listen_irc(self):
        ''' Listen for heartbeat, raise error if not heartbeat message '''
        while True:
            msg = await self.reader.readline().strip()
            if is_heartbeat(msg):
                await heartbeat(self, msg)
            else:
                # Print the message to user
                Logger.log(msg)


    async def close(self):
        ''' Close the messenger '''
        await self.writer.close()
