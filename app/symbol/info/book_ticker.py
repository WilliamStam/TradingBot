import asyncio
import aiohttp
import json
import aiomysql
import traceback
from app import app
from collections import namedtuple
from system.cli.output import (
    Line,
    Item
)
from app.fetch import fetch


async def book_ticker(ticker):
    endpoint = app.config.get("api.base") + "/v3/ticker/bookTicker"

    response = await ticker.fetch(endpoint,params={"symbol":ticker.symbol()})
    data = await response.json()

    return {
        "bidPrice": data.get('bidPrice'),
        "bidQty": data.get('bidQty'),
        "askPrice": data.get('askPrice'),
        "askQty": data.get('askQty'),
    }

