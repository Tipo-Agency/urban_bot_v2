import asyncio
from aiohttp import ClientSession

async def main():
    proxy = "http://46.19.64.193:8444"
    url = "http://icanhazip.com"

    async with ClientSession(proxy=proxy) as session:
        async with session.get(url) as response:
            print(await response.text())

asyncio.run(main())

