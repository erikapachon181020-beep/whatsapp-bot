import asyncio
import httpx

SHEET_ID = "1Iq4Y8lCSbSuJh-V-AsaE4MkQXPXc5OP2Y21_DHX2PYE"

async def test():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Catalogo"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.text[:800])

asyncio.run(test())