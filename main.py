import asyncio
import os

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from DB import Db

load_dotenv()

page_count = 64

host = os.environ.get('DB_HOST', '127.0.0.1')
port = os.environ.get('DB_PORT', '5432')
user = os.environ.get('DB_USER', 'root')
password = os.environ.get('DB_PASS', 'root')
db_name = os.environ.get('DB_NAME', 'mm')


async def get_item(url, name, session, db):
    async with session.get(url, verify_ssl=False) as response:
        page = await response.text()
        bs = BeautifulSoup(page, 'lxml')
        table = bs.find('table', class_='recipe_calculation')
        tfoot = table.find('tfoot').find_all('td', class_='variable')
        if float(tfoot[1].get_text()) < 50:
            return
        img = bs.find('img', class_='recipe_image_main')
        recipe = (name, float(tfoot[0].get_text()), float(tfoot[1].get_text()), f"https://daily-menu.ru{img.get('src')}", url)
        items = table.find('tbody').find_all('tr')
        prods = [it.find('td').get_text() for it in items]
        weight = [float(it.find('td', class_='variable').get_text()) for it in items]
        await db.new_recipe((recipe, prods, weight))
        # print(recipe, prods, weight)


async def main():
    db = Db()
    # db = ''
    await db.connect(host, port, user, password, db_name)
    last_title = await db.get_last_recipe()
    print(last_title)
    # last_title = ''
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
                tasks.append(asyncio.create_task(get_item(f'https://daily-menu.ru{item.find("a").get("href")}', name, session, db)))
            await asyncio.gather(*tasks)
            # print(f'added {25 * i+1} recipes')
            if if_exit:
                break
    await db.disconnect()


asyncio.run(main())
