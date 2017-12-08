''' handshake '''

from ..config import NICK

async def handshake(messenger):
    ''' Perform handshake with IRC server '''

    num_tries = 10
    sending_nick = True
    while sending_nick:
        if num_tries == 0:
            raise Exception('Failed to join server after 10 tries')
        # Generate NICK
        nick = messenger.make_nick()

        # Send NICK
        messenger.send('NICK {}'.format(nick))

        # Check for bad NICK
        if await messenger.invalid_nick():
            num_tries += 1
            continue

        # Send USER
        messenger.send('USER {0} 8 * :'.format(NICK))

        if await messenger.invalid_nick():
            num_tries += 1
            continue

        break

    # Send JOIN
    messenger.join()

    # Authenticate
    messenger.authenticate()
