''' utils/parse.py '''

import argparse

def parse_args():
    '''
    Parse the command line arguments

    Expected:
    hostname: string
    port: number
    channel: string
    secret-phrase: string
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help='the host of IRC server', type=str)
    parser.add_argument('port', help='the port of IRC server', type=int)
    parser.add_argument('channel', help='the channel of the IRC server to connect to', type=str)
    parser.add_argument('secret_phrase', help='the secret phrase used for authorization with bots', type=str)

    return parser.parse_args()

