import asyncio
import sys

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from DB import Db

page_count = 64


async def get_item(url, name, session, db):
    async with session.get(url, verify_ssl=False) as response:
        page = await response.text()
        bs = BeautifulSoup(page, 'lxml')
        table = bs.find('table', class_='recipe_calculation')
        tfood = table.find('tfoot').find_all('td', class_='variable')
        img = bs.find('img', class_='recipe_image_main')
        recipe = (name, tfood[0].get_text(), tfood[1].get_text(), img.get('src'))
        items = table.find('tbody').find_all('tr')
        prods = [it.find('td').get_text() for it in items]
        weight = [(it.find('td', class_='variable').get_text(),) for it in items]
        # await db.new_recipe(recipe, prods, weight)
        print(recipe, prods, weight)

async def main():
    # db = Db()
    db = ''
    # await db.connect()
    # last_title = await db.get_last_recipe()
    last_title = ''
    if_exit = False
    async with ClientSession() as session:
        for i in range(page_count):
            async with session.get(f'https://daily-menu.ru/dailymenu/recipes/index?DailymenuRecipes_page={i}&pageSize=25&DailymenuRecipes_sort=create_time', verify_ssl=False) as response:
                page = await response.text()
                tasks = []
            for item in BeautifulSoup(page, 'lxml').find_all('article', class_='recipe_anounce'):
                a = item.find('h4', class_='title').find('a')
                name = a.get_text()
                if name == last_title:
                    if_exit = True
                    break
                tasks.append(asyncio.create_task(get_item(f'https://daily-menu.ru/{item.find("a").get("href")}', name, session, db)))
            await asyncio.gather(*tasks)
            if if_exit:
                break


asyncio.run(main())