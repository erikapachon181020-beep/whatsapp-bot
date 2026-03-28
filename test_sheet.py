import asyncio
import httpx

SHEET_ID = "1N3xGYFlSsKrUFV6JtrkeBQ_Acc-9ypXlNc9H74qT7N8"
GID = "422848174"

async def test():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.text[:1000])

asyncio.run(test())