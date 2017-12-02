''' heartbeat '''

import re

async def heartbeat(messenger, line):
    ''' Deal with a PING from IRC client '''

    # Parse the message
    message = line.split('PING:', 1)

    # Send the PONG
    await messenger.send('PONG:{0}'.format(message))

def is_heartbeat(line):
    ''' determine if line is a heartbeat '''
    pattern = re.compile(r'^PING.*$')
    return bool(pattern.match(line))
