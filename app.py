def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        while True:
            try:
                await dp.start_polling(bot, handle_signals=False)
            except Exception as e:
                logging.error(f"Polling crashed: {e}")
                await asyncio.sleep(5)

    loop.run_until_complete(runner())
