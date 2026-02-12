import httpx

async def fetch_subscription(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text
