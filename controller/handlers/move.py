''' move handler '''

from argparse import ArgumentParser

from ..utils import Logger

async def move_handle(messenger, line):
    ''' Handle the move command '''

    # Parse line
    raw_args = line.split(' ')[1:]

    # Setup argparse
    parser = ArgumentParser(description='Parser for move commands')
    parser.add_argument('host_name', help='The hostname of the server to move the bots to')
    parser.add_argument('port', help='the port of the server to move the bots to', type=int)
    parser.add_argument('channel', help='the channel of the server to move the bots to')
    args = parser.parse_args(raw_args)

    Logger.log('issuing move...')

    # Send message to IRC server
    messenger.send_channel('move {0} {1} {2}'.format(args.host_name, args.port, args.channel))

    # Read responses & perform analytics
    responses = await messenger.read('move')
    failures = list(response for response in responses if 'fail' in response)

    Logger.logline()
    if not responses:
        Logger.log('Move failed (No bots)')
    else:
        Logger.log('Bots moved successfully: {}/{}'.format((len(responses) - len(failures)), len(responses)))
    Logger.logline()
