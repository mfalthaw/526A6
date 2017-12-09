''' Auth handler '''

async def auth_handle(messenger, _):
    ''' handle auth command '''
    messenger.authenticate()
