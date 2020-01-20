from pypika import Query, Table, Schema, Parameter, Order




class DbHandler:
    def __init__(self, pg_pool=None, cfg=None):
        self._pg_pool = pg_pool
        self._cfg = cfg

    async def _with_transaction(self, query: str, args: list, query_type='execute'):
        async with self._pg_pool.acquire() as conn:
            async with conn.transaction():
                if query_type == 'execute':
                    return await conn.execute(query, *args)
                if query_type == 'fetch':
                    return await conn.fetch(query, *args)
                return None


    async def _fetch(self, query: str, args: str):
        return await self._with_transaction(query, args, query_type='fetch')

    async def _execute(self, query: str, args: list):
        return await self._with_transaction(query, args, query_type='execute')



    @property
    def Q(self):
        return Query

    @property
    def S(self):
        return Schema

    @property
    def T(self):
        return Table

    @property
    def P(self):
        return Parameter

    @property
    def Order(self):
        return Order
    
    @property
    def schema(self):
        return self.S(self._cfg.SCHEMA_NAME)

    def table(self, table_name):
        return self.schema.__getattr__(table_name)

    def from_table(self, table_name):
        return self.Q.from_(self.table(table_name))

    async def insert_to_table(self, table_name: str, cols: dict, ignore_conflict=[]):
        keys = list(cols.keys())
        args = [cols[_] for _ in keys]
        params = [self.P('$' + str(_ + 1)) for _ in range(len(keys))]
        q = self.Q.into(self.table(table_name)).columns(*keys).insert(*params)
        query = str(q)
        if len(ignore_conflict) > 0 :
            ignore_conflict_str = ','.join(ignore_conflict)
            query += f'\nON CONFLICT ({ignore_conflict_str}) DO NOTHING'
        return await self._execute(query, args)


    async def fetch(self, query, args: list):
        return await self._fetch(str(query), args)

    async def execute(self, query, args: list):
        return await self._execute(str(query), args)


