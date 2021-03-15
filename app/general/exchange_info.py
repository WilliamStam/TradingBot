import asyncio
import aiohttp
import json
import random
from system.cli.output import (
    Line,
    Item
)
from app import app
from app.fetch import fetch
from system.requests import requests

async def exchange_info( ):
    endpoint = app.config.get("api.base") + "/v3/exchangeInfo"
    # response = await requests.get(endpoint, auth=aiohttp.BasicAuth('user', 'password'))
    response = await fetch(endpoint)
    data = await response.json()

    await save_symbols(data.get("symbols", list()))

    return len(data.get("symbols", list()))


async def save_symbols(symbols=list()):
    output = Line()
    # print(symbols)
    await app.db.execute("UPDATE symbols SET trading='0'")

    symbols_list = [{
        "symbol":c['symbol']
    } for c in symbols if c['status']=='TRADING']

    await app.db.executemany("""
        INSERT INTO symbols (
        symbol,
        trading
        ) VALUES (
            %(symbol)s,
            '1'
        ) ON DUPLICATE KEY UPDATE
            trading = VALUES(trading)
    """,symbols_list)

    output.add( Item("Saved Symbols",len(symbols_list)))

    output.print("\n")