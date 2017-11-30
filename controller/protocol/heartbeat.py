''' heartbeat '''

async def heartbeat(messenger, line):
    ''' Deal with a PING from IRC client '''

    # Parse the message
    message = line.split(str='PING:', num=1)

    # Send the PONG
    await messenger.write('PONG:{0}'.format(message))
