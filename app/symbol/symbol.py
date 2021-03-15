import asyncio
import aiohttp
import random
import time
import os
import psutil
import json
import traceback
import collections


from system import Requests
from system.db import Mysql
from system.timer import Timer
from system.config import Config
from system.utils.dict import merge_dicts
import signal

from app import app
from .info.price import price
from .info.book_ticker import book_ticker


from system.cli.output import (
    Line,
    Item
)

async def tes(process):
    print("hi",process.symbol())
    return {
        "fish":"cakes"
    }

async def asyncRunSymbol( symbol=None, loop=None ):
    async with RunSymbolContextManager(loop,symbol) as process:
        config = await process.config()
        while config is not False:
            config = await process.config()
            if config is False:
                print("Symbol shouldn't run any more", process.symbol(), process.pid())
                break
            async with SymbolLoopContextManager(process) as ticker:
                try:

                    ticker.output.add( Item("Pair",ticker.symbol(),format="{:<15}"), key="pair")
                    ticker.output.add( Item("Time", 0, format=['{:.2f}', '{:>6}']), key="time")
                    ticker.output.add( Item("Mem", process.mem(), format=['{:.2f}', '{:>6}']), key="mem")

                    ticker_data = {
                        "symbol":process.symbol(),
                        "price":None,
                        "bidPrice":None,
                        "bidQty":None,
                        "askPrice":None,
                        "askQty":None,
                    }
                    results = await asyncio.gather(
                        price(ticker),
                        book_ticker(ticker),
                    )


                    # super_dict = collections.defaultdict(set)
                    for d in results:
                        ticker_data = merge_dicts(ticker_data,d)

                    await process.db().execute(f"""
                        INSERT INTO data_ticker  (
                            `symbol`,
                            `datetime`,
                            `price`,
                            `bidPrice`,
                            `bidQty`,
                            `askPrice`,
                            `askQty`
                        ) VALUES (
                            %(symbol)s,
                            now(),
                            %(price)s,
                            %(bidPrice)s,
                            %(bidQty)s,
                            %(askPrice)s,
                            %(askQty)s
                        ) 
                    """, ticker_data)

                    ticker.output.add(Item("UsedWeight", ticker.fetch_weight, format="{:<4}"), key="weight")
                    ticker.output.add(Item("Price", ticker_data['price'], format="{:>15}"))
                    ticker.output.add(Item("bidPrice", ticker_data['bidPrice'], format="{:>15}"))
                    ticker.output.add(Item("bidQty", ticker_data['bidQty'], format="{:>15}"))
                    ticker.output.add(Item("askPrice", ticker_data['askPrice'], format="{:>15}"))
                    ticker.output.add(Item("askQty", ticker_data['askQty'], format="{:>15}"))

                except Exception as e:
                    exception_type = type(e).__name__
                    stack = traceback.extract_stack() + traceback.extract_tb(e.__traceback__)
                    pretty = traceback.format_list(stack)[-5:]

                    bits = list()
                    bits.append("*" * 15 + " SAVING TICKER ERROR " + "*" * 15)
                    bits.append(str(e))
                    bits.append(exception_type)
                    bits.append(json.dumps(pretty, indent=2))
                    bits.append("*" * 37)

                    print("\n".join(bits))

                ticker.output.update('time', value=ticker.timers.total())
                ticker.output.print(" | ")
                await asyncio.sleep(config.get("interval"))



            if not await process.running():
                print("PROCESS ISNT RUNNING ANY MORE",process.symbol(),process.pid())
                break


def RunSymbol( symbol=None ):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncRunSymbol(symbol=symbol,loop=loop))
    except Exception as e:
        print(f"Exception: {e}")



class RunSymbolContextManager:
    def __init__( self, loop, symbol=None ):

        self._symbol = symbol
        self._loop = loop
        self._process_id = os.getpid()

        self._db = Mysql(
            loop=loop,
            host=app.config.get("db.host"),
            database=app.config.get("db.database"),
            user=app.config.get("db.username"),
            password=app.config.get("db.password"),
            port=app.config.get("db.port"),
            charset=app.config.get("db.charset"),
            connect_timeout=app.config.get("db.connection_timeout ") or 900,
        )

        self._requests = Requests()

    def symbol( self ):
        return self._symbol

    def pid( self ):
        return self._process_id

    def db( self ):
        return self._db

    def loop( self ):
        return self._loop

    async def fetch( self,endpoint, **kwargs ):
        response = await self._requests.get(endpoint, **kwargs)
        output = Line()
        output.add(Item("FETCH", response.url), key="endpoint")
        output.add(Item("STATUS", response.status), key="status")
        for h in response.headers:
            if h.startswith("x-mbx-used-weight"):
                output.add(Item(h, response.headers[h]), key=h)
        # output.print(" | ")

        # print(response)

        return response

    def mem( self ):
        return psutil.Process(self.pid()).memory_info().rss / 2. ** 20

    async def update( self ):
        # if type(data) == dict:
        #     data = json.dumps(data)

        await self.db().execute("""
            UPDATE running SET
                `symbol` = %(symbol)s,
                `process_id` = %(process_id)s,
                `updated` = now()
            WHERE
                `symbol` = %(symbol)s
        """, {
            "symbol": self.symbol(),
            "process_id": self.pid(),
        })

    async def config( self ):
        # if type(data) == dict:
        #     data = json.dumps(data)
        conf = False
        try:
            is_active_data = await self.db().query("""
                   SELECT
                        symbols.symbol,
                        symbols.config
                   FROM `symbols`
                        LEFT JOIN users_symbols ON users_symbols.symbol = symbols.symbol

                   WHERE symbols.trading = '1' AND users_symbols.enabled = '1' AND symbols.symbol = %(symbol)s
                   GROUP BY symbols.symbol
               """, {
                "symbol": self.symbol()
            })

            is_active_data = is_active_data.first()

            if is_active_data:
                if is_active_data.get('symbol'):
                    symbol_conf = is_active_data.get("config","{}") or "{}"
                    config = Config()
                    config.load(app.config.get("symbol"),json.loads(symbol_conf))
                    conf = config

        except Exception as e:
            exception_type = type(e).__name__
            stack = traceback.extract_stack() + traceback.extract_tb(e.__traceback__)
            pretty = traceback.format_list(stack)[-4:]


            print("config exception",exception_type,str(e),pretty)
        # print("CONFIG", conf)
        return conf

    async def running( self ):
        # if type(data) == dict:
        #     data = json.dumps(data)

        is_running = False

        try:
            is_data = await self.db().query("""
                   SELECT
                        count(*) as c
                   FROM `running`
                   WHERE running.symbol = %(symbol)s
               """, {
                "symbol": self.symbol()
            })
            is_running = True if is_data[0]['c'] else False
        except:
            pass

        return is_running

    async def __aenter__( self ):
        print(f"Starting: {self.symbol()} [{self.pid()}]")
        await self.db().execute("""
            INSERT INTO running (
                `symbol`,
                `process_id`,
                `updated`,
                `started`
            ) VALUES (
                %(symbol)s,
                %(process_id)s,
                NOW(),
                NOW()
            ) ON DUPLICATE KEY UPDATE
                `process_id` = VALUES(`process_id`)
        """, {
            "process_id": self.pid(),
            "symbol": self.symbol(),

        })
        return self

    async def __aexit__( self, exc_type, exc_value, exc_tb ):
        print(f"Ending: {self.symbol()} [{self.pid()}]")
        await self.db().execute("DELETE FROM running WHERE symbol = %(symbol)s", {
            "symbol": self.symbol()
        })

class SymbolLoopContextManager:
    def __init__( self, process ):
        self._process = process
        self.timers = None
        self.output = None
        self.fetch_weight = 0

    def __getattr__( self, attr ):

        # print("*"*30,attr)
        return getattr(self._process, attr)

    async def fetch( self, endpoint, **kwargs ):
        ret = await self._process.fetch(endpoint,**kwargs)
        if int(ret.headers['x-mbx-used-weight']) > self.fetch_weight:
            self.fetch_weight = int(ret.headers['x-mbx-used-weight'])
        return ret

    async def __aenter__( self ):
        # print(f"Running: {self._process.symbol()} [{self._process.pid()}]")

        self.timers = Timer()
        self.output = Line()
        self.fetch_weight = 0


        self.timers.start("Loop")
        await self._process.update()
        return self

    async def __aexit__( self, exc_type, exc_value, exc_tb ):
        await self._process.update()
        self.timers.stop("Loop")
        # print(f"Finished: {self._process.symbol()} [{self._process.pid()}]", self.timers.show())