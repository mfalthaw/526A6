#!/usr/bin/env python
''' bot.py '''

import argparse
import sys

# globals
DEBUG = True

class Bot():
    def __init__(self):
        # init bot
        raise NotImplementedError()


def parse_args():
    '''
    Handles parsing arguments
    Reference: https://docs.python.org/3/library/argparse.h
    '''
    usage = 'python3 bot.py <hostname> <port> <channel> <secret-phrase>'
    parser = argparse.ArgumentParser(usage=usage)

    # expected arguments
    parser.add_argument(
        'hostname',
        type=str,
        help='The <hostname> specifies the IRC server\’s hostname.'
    )
    parser.add_argument(
        'port',
        type=int,
        help='The <port> specifies the port for the IRC server\'s hostname'
    )
    parser.add_argument(
        'channel',
        type=str,
        help='The <channel> specifies which IRC channel the bot will join.'
    )
    parser.add_argument(
        'secret_phrase',
        type=str,
        help='The <secret-phrase> specifies some secret text that the IRC bot will listen for.'
    )

    args = parser.parse_args()
    if args.port not in range(0, 65536):
        log('Error: port must be 0-65535.')
        parser.exit('Usage: ' + usage)

    return args

def log(msg):
    ''' Log a debug message '''
    if DEBUG:
        print(msg, file=sys.stderr)

def main():
    args = parse_args()
    log(args.hostname)
    log(args.port)
    log(args.channel)
    log(args.secret_phrase)        
    

if __name__ == '__main__':
    main()