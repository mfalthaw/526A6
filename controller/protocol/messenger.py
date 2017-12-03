''' protocol messenger '''

import asyncio

from .heartbeat import heartbeat, is_heartbeat
from ..utils import Logger

class Messenger:
    ''' Handle messages between IRC server and client '''

    def __init__(self, reader, writer, channel):
        self.__reader = reader
        self.__writer = writer
        self.__channel = channel
        self.__responses = []

    async def send(self, msg):
        ''' send message to IRC server '''
        payload = ('{0}\r\n'.format(msg)).encode('utf_8')
        self.__writer.write(payload)
        Logger.debug('--> {}'.format(payload))
        return

    async def read(self, key=None):
        ''' Read responses from bots '''
        fut = self.__read_response()

        # Listen for responses from bots for 3 seconds
        try:
            await asyncio.wait_for(fut, timeout=3)
        except asyncio.TimeoutError:
            pass

        # Collect the responses
        responses = self.__responses
        self.__responses = []

        # Parse the messages TODO: check if we should remove this
        # (might not be necessary if irc does this)
        responses = filter(lambda line: 'PRIVMSG' in line, responses)
        responses = map(lambda line: line.split(' :', 1), responses)

        # Filter if necessary
        if key:
            responses = filter(lambda line: key in line, responses)

        # Return the responses
        return list(responses)


    async def send_channel(self, msg):
        ''' send a private message to channel '''
        return await self.send('PRIVMSG #{0} :{1}'.format(self.__channel, msg))

    async def join(self):
        ''' Join the channel '''
        return await self.send('JOIN :#{}'.format(self.__channel))

    async def send_quit(self):
        ''' Send quit message '''
        return await self.send('QUIT')

    async def listen_irc(self):
        ''' Listen for heartbeat, raise error if not heartbeat message '''
        while True:
            msg = await self.__read_line()
            if is_heartbeat(msg):
                await self.__heartbeat(msg)
            else:
                # Log that the message was not received, else print msg to user
                Logger.debug('<-- {}'.format(msg))


    def close(self):
        ''' Close the messenger '''
        self.__writer.close()

    async def __read_response(self):
        while True:
            msg = await self.__read_line()
            if is_heartbeat(msg):
                await self.__heartbeat(msg)
            else:
                # Collect the message
                self.__responses.append(msg)

    async def __heartbeat(self, msg):
        Logger.debug('<-- {}'.format(msg))
        await heartbeat(self, msg)


    async def __read_line(self):
        return (await self.__reader.readline()).decode('utf_8').strip()
