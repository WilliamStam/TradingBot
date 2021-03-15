
from system.cli.output import (
    Line,
    Item
)
from app import app

async def fetch( endpoint, **kwargs ):
    response = await app.exchange.get(endpoint,**kwargs)
    output = Line()
    output.add(Item("FETCH", response.url), key="endpoint")
    output.add(Item("STATUS", response.status), key="status")
    for h in response.headers:
        if h.startswith("x-mbx-used-weight"):
            output.add(Item(h, response.headers[h]), key=h)
    output.print("\n")

    # print(response)

    return response
