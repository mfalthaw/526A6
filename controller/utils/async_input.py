''' async input reader '''

import select
import asyncio
import sys

from ..utils import Logger

class AsyncInput:
    ''' Class to read from input async '''

    def __init__(self, input_reader=None, input_writer=None):
        self.__reader = input_reader
        self.__writer = input_writer


    async def read(self, message):
        '''
        Read from stdin async
        * only works on unix

        Thanks to https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
        '''
        Logger.log('=== {} ==='.format(message))

        while True:
            user_input = select.select([sys.stdin], [], [], 0)[0]
            if user_input:
                line = sys.stdin.readline().replace('\n', '')
                return line
            else:
                await asyncio.sleep(1 / 300)
