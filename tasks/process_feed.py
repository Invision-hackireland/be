import asyncio


async def background_loop():
    while True:
        await asyncio.sleep(1)
        # processor.process()