''' handshake '''

from ..config import NICK, USER

async def handshake(messenger, secret):
    ''' Perform handshake with IRC server '''

    # Send NICK
    await messenger.send('NICK {0}'.format(NICK))

    # Send USER
    await messenger.send('USER {0} 0 * :Real name'.format(USER))

    # Send JOIN
    await messenger.join()

    # Authenticate
    await messenger.send_channel(secret)
