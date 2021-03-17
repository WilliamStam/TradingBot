import traceback
import asyncio
import aiomysql
import pymysql


class Mysql:
    """A lightweight wrapper around aiomysql.Pool for easy to use
    """

    def __init__( self,

        host,
        port,
        database,
        user,
        password,
        app=None,
        loop=None,
        return_dict=True,
        pool_recycle=7 * 3600,
        autocommit=True,
        charset="utf8mb4",
        **kwargs
    ):
        '''
        kwargs: all parameters that aiomysql.connect() accept.
        '''
        self.db_args = {
            'host': host,
            'port': int(port),
            'db': database,
            'user': user,
            'password': password,
            'charset': charset,
            'loop': loop,
            'autocommit': autocommit,
            'pool_recycle': pool_recycle,
        }

        if return_dict:
            self.db_args['cursorclass'] = aiomysql.cursors.DictCursor
        if kwargs:
            self.db_args.update(kwargs)

        self.pool = None
        self.app = app
        if loop:
            self.db_args['loop'] = loop

    async def init_pool( self ):
        if self.app:
            self.db_args['loop'] = self.app.loop

        self.pool = await aiomysql.create_pool(**self.db_args)

    async def query_many( self, queries ):
        """query man SQL, Returns all result."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                results = []
                for query in queries:
                    try:
                        await cur.execute(query)
                        ret = await cur.fetchall()
                    except pymysql.err.InternalError:
                        await conn.ping()
                        await cur.execute(query)
                        ret = await cur.fetchall()
                    results.append(MysqlResponse(ret))
                return results

    async def query( self, query, parameters=dict()):
        """Returns a row list for the given query and parameters."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query, parameters)
                    ret = await cur.fetchall()
                except pymysql.err.InternalError:
                    await conn.ping()
                    await cur.execute(query, parameters)
                    ret = await cur.fetchall()

                return MysqlResponse(ret)

    async def get( self, query, parameters=dict() ):
        """Returns the (singular) row returned by the given query.
        """
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query, parameters)
                    ret = await cur.fetchone()
                except pymysql.err.InternalError:
                    await conn.ping()
                    await cur.execute(query, parameters)
                    ret = await cur.fetchone()
                return ret

    async def execute( self, query, parameters=dict()):
        """Executes the given query, returning the lastrowid from the query."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query, parameters)
                except Exception:
                    # https://github.com/aio-libs/aiomysql/issues/340
                    await conn.ping()
                    await cur.execute(query, parameters)
                return cur.lastrowid


    async def executemany( self, query, parameters=list()):
        """Executes the given query, returning the lastrowid from the query."""
        if not self.pool:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.executemany(query, list(parameters))
                    # await conn.commit()
                except Exception:
                    # https://github.com/aio-libs/aiomysql/issues/340
                    await conn.ping()
                    await cur.executemany(query, parameters)
                    # await conn.commit()
                # return cur.lastrowid




from collections.abc import Sequence
import json
class MysqlResponse(Sequence):
    def __init__(self, cursor):
        self.data = list()
        self.__cursor = cursor
        if cursor:
            try:
                self.data = list(cursor)
            except:
                self.data = list()

    def __getitem__(self, index):
        return self.data[index]
    def __len__(self):
        return len(self.data) or 0
    def __bool__(self):
        return bool(self.__cursor)
    def __str__(self):
        return json.dumps(self.data,default=str,indent=4)
    def __dict__(self):
        return json.dumps(self.data,default=str,indent=4) or {}

    def first(self):
        if self.data:
            return self.data.pop()




