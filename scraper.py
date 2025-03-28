#%%
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
import nest_asyncio

nest_asyncio.apply()

base_url = "https://vlf.ap.dias.ie/data/dunsink/"

async def fetch(session, url):
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        print(f"[!] Invalid URL skipped: {url}")
        return ""

    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"[!] Failed to fetch {url} - Status: {response.status}")
                return ""
    except aiohttp.ClientError as e:
        print(f"[!] Request failed for {url}: {e}")
        return ""

async def scrape_directory(session, url, parent_dir, output_file):
    html = await fetch(session, url)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    tasks = []
    for link in links:
        href = link.get('href')
        if href and href not in ['../', '/']:
            if href and href not in ['../', '/']:
                full_url = urllib.parse.urljoin(url, href)

            # Only continue if the URL is within the base domain
            if not full_url.startswith(base_url):
                continue

            full_path = urllib.parse.urljoin(parent_dir, href)


            if href.endswith('/'):
                # Check if directory path contains both keywords
                if "super_sid" in full_path and "csv" in full_path:
                    print(f"[+] Found matching directory: {full_path}")
                    output_file.write(f"{full_path}\n")

                # Recurse into subdirectory
                task = asyncio.ensure_future(scrape_directory(session, full_url, full_path, output_file))
                tasks.append(task)

    await asyncio.gather(*tasks)

async def main():
    output_filename = "supersid_directories.txt"
    with open(output_filename, "w") as output_file:
        async with aiohttp.ClientSession() as session:
            await scrape_directory(session, base_url, base_url, output_file)

asyncio.run(main())
