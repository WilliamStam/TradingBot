import asyncio
import time
import psutil
import sys
import signal

from concurrent.futures import ThreadPoolExecutor

from app import (
    app,
    CreateApp,
)
from app.symbol import RunSymbol
from app.general.exchange_info import exchange_info
from system.db import Mysql



CreateApp()


async def startup():
    print("-"*5," STARTUP ","-"*5)

    return [
        await exchange_info()
    ]



async def shutdown():
    print("-" * 5, " SHUTDOWN ", "-" * 5)
    await app.db.execute("TRUNCATE TABLE running")


async def active_symbols():
    system_pids = [str(x) for x in psutil.pids()]
    running = await app.db.query("SELECT process_id FROM running")
    orphaned_running = [str(x['process_id']) for x in running if str(x['process_id']) not in system_pids]
    if len(orphaned_running):
        print("CLEANING ORPHAN RUNNING:", orphaned_running)
        for row in orphaned_running:
            await app.db.query("DELETE FROM running WHERE process_id = %(process_id)s", {
                "process_id": row
            })


    return [{
        "symbol": x['symbol'],
        "running": True if str(x['running'])=='1' else False
    } for x in await app.db.query("""
       SELECT
           symbols.symbol,
           IF(running.symbol is null,0,1) as running
       FROM `symbols`
       LEFT JOIN users_symbols ON users_symbols.symbol = symbols.symbol
       LEFT JOIN running ON running.symbol = symbols.symbol

       WHERE symbols.trading = '1' AND users_symbols.enabled = '1'
       GROUP BY symbols.symbol
   """)]

if __name__ == '__main__':

    max_workers, = app.loop.run_until_complete(startup())
    ex = ThreadPoolExecutor(max_workers=max_workers)

    while True:
        symbols = app.loop.run_until_complete(active_symbols())
        # print("ACTIVE:",symbols)
        for symbol in symbols:
            if not symbol.get("running"):
                # print("Need to start:",symbol.get("symbol"))
                ex.submit(RunSymbol, symbol=symbol.get('symbol'))

        try:
            time.sleep(15)
        except KeyboardInterrupt:
            print("Main loop detected a ctrl+c")
            break;

    app.loop.run_until_complete(shutdown())
        # if symbol.get("symbol") not in running_symbols:
        #     pass


    #
    #
    # for symbol in symbols:
    #     res = ex.submit(RunSymbol, symbol=symbol.get('symbol'))







    #
    # executor = ProcessPoolExecutor()
    # asyncio.get_event_loop().run_until_complete(main(executor))


