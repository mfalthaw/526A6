''' handshake '''

import uuid

from ..config import NICK
from ..utils import Logger

async def handshake(messenger, secret):
    ''' Perform handshake with IRC server '''

    num_tries = 10
    sending_nick = True
    while sending_nick:
        if num_tries == 0:
            raise Exception('Failed to join server after 10 tries')
        # Generate NICK
        nick = '{0}-{1}'.format(NICK, uuid.uuid4())

        # Send NICK
        messenger.send('NICK {}'.format(nick))
        # Send USER
        messenger.send('USER {0} 8 * :'.format(NICK))

        response = await messenger.read_line()

        for seg in response.split(':')[1:2]:
            if '433' in seg:
                Logger.debug('*** Nick taken: {}, retrying... ***'.format(nick))
                continue

            elif '001' in seg:
                Logger.debug('*** Nick accepted ***')
                sending_nick = False
                break

        num_tries += 1

    # Send JOIN
    messenger.join()

    # Authenticate
    messenger.send_channel(secret)
