''' async input reader, reference from: https://gist.github.com/nathan-hoad/8966377 '''

import os
import asyncio
from asyncio.streams import StreamWriter, FlowControlMixin
import sys


class Input:
    ''' Class to read from input async '''

    def __init__(self, input_reader=None, input_writer=None):
        self.reader = input_reader
        self.writer = input_writer

    async def async_input(self, message):
        ''' Read from stdin async '''
        if isinstance(message, str):
            message = message.encode('utf8')

        if (self.reader, self.writer) == (None, None):
            reader, writer = await self.__stdio()

        writer.write(message)
        await writer.drain()

        line = await reader.readline()
        return line.decode('utf8').replace('\r', '').replace('\n', '')

    async def __stdio(self, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        reader = asyncio.StreamReader()
        reader_protocol = asyncio.StreamReaderProtocol(reader)

        writer_transport, writer_protocol = await loop.connect_write_pipe(FlowControlMixin, os.fdopen(1, 'wb'))
        writer = StreamWriter(writer_transport, writer_protocol, None, loop)

        await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

        return reader, writer
