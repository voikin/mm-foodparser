import asyncio

from aiohttp import ClientSession
from bs4 import BeautifulSoup

page_count = 64

async def get_item(url, session):
    async with session.get(url, verify_ssl=False) as response:
        page = await response.text()
        bs = BeautifulSoup(page, 'lxml').find('table', class_='recipe_calculation').find('tbody').find_all('tr')
        a = bs[0].find('td')
        b = [i for i in bs[0].find_all('td', class_='variable')]
        return {it.find('td').get_text(): [i.get_text() for i in it.find_all('td', class_='variable')] for it in bs}



async def main():
    async with ClientSession() as session:
        for i in range(page_count):
            async with session.get(f'https://daily-menu.ru/dailymenu/recipes/index?DailymenuRecipes_page={i}&pageSize=25', verify_ssl=False) as response:
                page = await response.text()
                tasks = []
            for item in BeautifulSoup(page, 'lxml').find_all('article', class_='recipe_anounce'):
                tasks.append(asyncio.create_task(get_item(f'https://daily-menu.ru/{item.find("a").get("href")}', session)))
            ans = await asyncio.gather(*tasks)
            print(ans)


asyncio.run(main())