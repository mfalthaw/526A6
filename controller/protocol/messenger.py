''' protocol messenger '''

import asyncio

from .heartbeat import heartbeat, is_heartbeat
from ..utils import Logger
from ..errors import QuitSignal

class Messenger:
    ''' Handle messages between IRC server and client '''

    @classmethod
    async def create(cls, channel, host, port):
        ''' Create instance of messenger and connect '''
        self = Messenger(channel, host, port)
        await self.__connect()
        return self

    def __init__(self, channel, host, port):
        self.__reader = None
        self.__writer = None
        self.__channel = channel
        self.__host = host
        self.__port = port
        self.__responses = []

    def send(self, msg):
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

    async def read_line(self):
        ''' Read a line '''
        msg = await self.__read_line()
        Logger.debug('<-- {}'.format(msg))
        return msg

    def send_channel(self, msg):
        ''' send a private message to channel '''
        return self.send('PRIVMSG #{0} :{1}'.format(self.__channel, msg))

    def join(self):
        ''' Join the channel '''
        return self.send('JOIN :#{}'.format(self.__channel))

    async def send_quit(self):
        ''' Send quit message '''
        return self.send('QUIT')

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

        msg = await self.__reader.readline()

        if not msg:
            # Server disconnected, attempt new connection
            self.__reconnect()
        else:
            return msg.decode('utf_8').strip()

    async def __connect(self):
        ''' Attempt to make connection to server '''
        try:
            self.__reader, self.__writer = await asyncio.wait_for(asyncio.open_connection(self.__host, self.__port, loop=asyncio.get_event_loop()), timeout=3)
        except asyncio.TimeoutError:
            raise QuitSignal()

    async def __reconnect(self):
        ''' Upon losing connection to server, attempt to reconnect '''
        Logger.debug('*** Connection lost, reconnecting... ***')
        try:
            self.__reader, self.__writer = await self.__connect()
        except QuitSignal:
            Logger.log('--- Timed out attempting to reconnect to server ---')
            raise
