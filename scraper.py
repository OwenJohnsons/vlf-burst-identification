#%%
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
import nest_asyncio

nest_asyncio.apply()

base_url = "https://vlf.ap.dias.ie/data/"

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def scrape_directory(session, url, parent_dir, output_file):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'html.parser')
    
    links = soup.find_all('a')

    tasks = []
    for link in links:
        href = link.get('href')
        if href and href not in ['../', '/']:
            if href.endswith('/'):
                directory_name = urllib.parse.urljoin(parent_dir, href)
                if "super_sid" in directory_name:
                    print(f"Found directory: {directory_name}")
                    output_file.write(f"{directory_name}\n")
                
                task = asyncio.ensure_future(scrape_directory(session, urllib.parse.urljoin(url, href), directory_name, output_file))
                tasks.append(task)
    
    await asyncio.gather(*tasks)

async def main():
    with open("supersid_directories.txt", "w") as output_file:
        async with aiohttp.ClientSession() as session:
            await scrape_directory(session, base_url, base_url, output_file)

asyncio.run(main())