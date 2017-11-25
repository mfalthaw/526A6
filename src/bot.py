#!/usr/bin/env python
''' bot.py '''

import argparse
import sys
import socket

# globals
DEBUG = True

class Bot():
    def __init__(self, hostname, port, channel, secret_phrase):
        # init bot
        self.hostname = hostname
        self.port = port
        self.channel = channel
        self.secret_phrase = secret_phrase
        self.irc_socket = None
        self.nick = 'spyBot'
    
    def __send_message(self, msg):
        self.irc_socket.send(msg.encode('utf-8'))
    
    def __connect_to_irc_server(self):
        '''
        connect to IRC server
        '''
        log('Connecting to: {}:{}'.format(self.hostname, int(self.port)))
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.irc_socket.connect((self.hostname, int(self.port)))
            except:
                log('Diconnected from: {}:{}'.format(self.hostname, int(self.port)))
            break
        self.__authenticate()
    
    def __authenticate(self):
        self.__send_message('USER ' + self.nick + ' ' + self.nick + ' ' + self.nick + ' :\n')
        self.__send_message('NICK ' + self.nick + '\n')
        # PRIVMSG <#channel>|<nick> :<message>
        # self.__send_message('PRIVMSG nickserv :iNOOPE\r\n')
        self.__send_message('JOIN #' + self.channel + '\n')
        self.__send_message('PRIVMSG hi from spybot01!')

    def start_bot(self):
        '''
        start bot
        source: https://stackoverflow.com/questions/2968408
        '''
        self.__connect_to_irc_server()



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
        help='The <hostname> specifies the IRC server\'s hostname.'
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
    
    # connect to IRC server
    log('Connecting to: {}:{}'.format(args.hostname, int(args.port)))
    conn = socket.socket()
    conn.connect((args.hostname, int(args.port)))

    # start bot
    bot = Bot(args.hostname, int(args.port), args.channel, args.secret_phrase)
    bot.start_bot()
    

if __name__ == '__main__':
    main()