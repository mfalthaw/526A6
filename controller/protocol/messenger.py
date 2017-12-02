''' protocol messenger '''

from .heartbeat import heartbeat, is_heartbeat
from ..utils import Logger

class Messenger:
    ''' Handle messages between IRC server and client '''

    def __init__(self, reader, writer, channel):
        self.__reader = reader
        self.__writer = writer
        self.__channel = channel

    async def send(self, msg):
        ''' send message to IRC server '''
        payload = ('{0}\r\n'.format(msg)).encode('utf_8')
        self.__writer.write(payload)
        return

    async def send_channel(self, msg):
        ''' send a private message to channel '''
        return await self.send('PRIVMSG {0} :{1}'.format(msg, self.__channel))

    async def join(self):
        ''' Join the channel '''
        return await self.send('JOIN :{}'.format(self.__channel))

    async def send_quit(self):
        ''' Send quit message '''
        return await self.send('QUIT')

    async def read(self):
        ''' Wait for a message from the IRC server '''
        while True:
            msg = await self.__read_line()
            msg = msg.strip()
            if is_heartbeat(msg):
                await heartbeat(self, msg)
                continue

            return msg

    async def listen_irc(self):
        ''' Listen for heartbeat, raise error if not heartbeat message '''
        while True:
            msg = await self.__read_line()
            if is_heartbeat(msg):
                await heartbeat(self, msg)
            else:
                # Print the message to user
                Logger.log(msg)


    def close(self):
        ''' Close the messenger '''
        self.__writer.close()

    async def __read_line(self):
        return (await self.__reader.readline()).decode('utf_8').strip()
