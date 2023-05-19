from asyncpg import create_pool

class Db:
    def __init__(self):
        self.pool = None
        self.recipe_table = 'recipe'
        self.product_table = 'product'
        self.product_recipe = 'product_recipe'

    async def connect(self, host, port, user, passwd, name):
        self.pool = await create_pool(
            host=host,
            port=port,
            user=user,
            password=passwd,
            database=name
        )


    async def get_last_recipe(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch(f'SELECT url FROM {self.recipe_table} order by id desc limit 1')

    async def _bulk_create_products(self, products):
        async with self.pool.acquire() as conn:
            return await conn.executemany(f'''INSERT INTO {self.product_table} (name) VALUES ($1)  ON CONFLICT (name) DO NOTHING RETURNING id;''', products)

    async def _create_recipe(self, recipe):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                f'''INSERT INTO {self.recipe_table} (name, weight, calories, img) VALUES ($1, $2, $3, $4) RETURNING id;''', recipe)

    async def new_recipe(self, recipe_data):
        recipe_id = await self._create_recipe(recipe_data[0])
        prods = await self._bulk_create_products(recipe_data[1])
        async with self.pool.acquire() as conn:
            for prod in zip(prods, recipe_data[2]):
                await conn.execute(f'''INSERT INTO {self.product_recipe} (recipe_id, product_id, weight) VALUES ($1, $2, $3)''', (recipe_id, prod[0], prod[1]))