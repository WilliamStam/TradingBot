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


async def price(ticker):
    endpoint = app.config.get("api.base") + "/v3/ticker/price"

    response = await ticker.fetch(endpoint,params={"symbol":ticker.symbol()})
    data = await response.json()

    return {
        "price":data['price']
    }

