''' status '''

async def status_handle(messenger):
    ''' Request status from the bots '''
    await messenger.send_channel('status')
