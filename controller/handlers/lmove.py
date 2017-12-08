''' lmove handler '''
from argparse import ArgumentParser

from ..utils import Logger

async def lmove_handle(messenger, line):
    ''' Handle lmove command '''
    # Parse line
    raw_args = line.split(' ')[1:]

    # Setup argparse
    parser = ArgumentParser(description='Parser for move commands')
    parser.add_argument('channel', help='The new channel to move to')
    args = parser.parse_args(raw_args)

    Logger.log('issuing move...')
    messenger.move(args.channel)
