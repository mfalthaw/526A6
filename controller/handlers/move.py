''' move handler '''

from argparse import ArgumentParser

async def move_handle(messenger, line):
    # Parse line
    raw_args = line.split(' ')[1:]

    # Setup argparse
    parser = ArgumentParser(description='Parser for move commands')
    parser.add_argument('host_name', help='The hostname of the server to move the bots to')
    parser.add_argument('port', help='the port of the server to move the bots to', type=int)
    parser.add_argument('channel', help='the channel of the server to move the bots to')
    args = parser.parse_args(raw_args)

    # Send message to IRC server
    await messenger.send_channel('move {0} {1} {2}'.format(args.host_name, args.port, args.channel))
