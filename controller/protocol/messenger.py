''' protocol messenger '''

import asyncio
import uuid

from .heartbeat import heartbeat, is_heartbeat
from ..utils import Logger
from ..errors import QuitSignal
from ..config import NICK

class Messenger:
    ''' Handle messages between IRC server and client '''

    @classmethod
    async def create(cls, channel, host, port):
        ''' Create instance of messenger and connect '''
        self = Messenger(channel, host, port)
        await self.__connect()
        return self

    def __init__(self, channel, host, port):
        self.__nick = None
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

        # Log the responses
        Logger.debugline()
        Logger.debug('*** Responses ***')
        for response in responses:
            Logger.debug(response)

        # Parse the messages
        responses = list(filter(lambda line: 'PRIVMSG' in line, responses))
        responses = list(map(lambda line: line.split(' :', 1)[1], responses))

        # Filter if necessary
        if key:
            responses = list(filter(lambda line: key in line, responses))

        Logger.debug('\n*** Filtered Responses ***')
        for response in responses:
            Logger.debug(response)

        # Return the responses
        return responses

    def get_nick(self):
        ''' Return nick '''
        return self.__nick

    def make_nick(self):
        ''' Generate a new nick and return '''
        if self.__nick is None:
            self.__nick = NICK
        else:
            self.__nick = '{}-{}'.format(NICK, uuid.uuid4())

        return self.__nick

    async def invalid_nick(self):
        ''' Check if the nick is invalid '''
        try:
            msg = await asyncio.wait_for(self.__read_line(), timeout=(1/10))
        except asyncio.TimeoutError:
            Logger.debug('*** Timed out waiting for invalid NICK ***')
            return False
        for seg in msg.split(':')[1:2]:
            if '433' in seg:
                Logger.debug('*** Server responded with invalid NICK ***')
                return True
            elif '001' in seg:
                Logger.debug('*** Server responded with valid NICK ***')
                return False

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
