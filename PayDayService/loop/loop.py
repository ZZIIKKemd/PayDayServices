async def process_loop(app):
    while True:
        try:
            await asyncio.sleep(1)

            nextMsg = await app['db'].get_next()
            nextSms = await app['db'].get_next_sms()
            if not nextMsg and not nextSms:
                continue

            now = datetime.now(gettz('Europe/Moscow'))

            if nextMsg:
                if now >= nextMsg['time']:
                    try:
                        await app['api'].add(
                            nextMsg['name'], nextMsg['email'],
                            nextMsg['phone'], nextMsg['list'])
                    except:
                        pass
                    else:
                        await app['db'].remove_entry(nextMsg['id'])

            if nextSms:
                if now >= nextSms['time']:
                    try:
                        await app['sms'].send_random_sim(
                            nextSms['text'], nextSms['phone'])
                    except Exception as e:
                        pass
                    else:
                        await app['db'].remove_sms(nextSms['id'])

        except asyncio.CancelledError:
            break
        except Exception as e:
            log_error('Неожиданная ошибка сервера: '+str(e))
            break
