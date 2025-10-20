#!/usr/bin/env python3
"""
Quick Blender File Scraper using GitHub Code Search API.
Much simpler and faster than the full scraper.
"""

import os
import json
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def scrape_blend_files():
    """Scrape .blend files from GitHub using code search."""
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("❌ Error: GITHUB_TOKEN not found in environment")
        return

    print("🚀 Starting GitHub .blend file scraper...")
    print(f"Token: {token[:15]}...\n")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    output_dir = Path("training_data/scraped")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "blend_files.json"

    all_files = []
    page = 1
    max_pages = 10  # Get first 1000 files (100 per page)

    async with aiohttp.ClientSession() as session:
        while page <= max_pages:
            # Use code search API with extension:blend
            url = f"https://api.github.com/search/code?q=extension:blend&per_page=100&page={page}"

            print(f"📡 Fetching page {page}/{max_pages}...")

            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get('items', [])
                        total = data.get('total_count', 0)

                        print(f"   Found {len(items)} files (total available: {total})")

                        for item in items:
                            file_info = {
                                "filename": item.get('name'),
                                "path": item.get('path'),
                                "repo": item.get('repository', {}).get('full_name'),
                                "url": item.get('html_url'),
                                "download_url": item.get('git_url'),
                                "size": item.get('size', 0),
                                "sha": item.get('sha')
                            }
                            all_files.append(file_info)

                        # If we got fewer items than requested, we've reached the end
                        if len(items) < 100:
                            print(f"\n✅ Reached end of results at page {page}")
                            break

                        page += 1
                        await asyncio.sleep(2)  # Rate limit protection

                    elif resp.status == 403:
                        print(f"\n⚠️  Rate limited at page {page}")
                        print("Saving what we have so far...")
                        break

                    else:
                        print(f"\n❌ Error {resp.status} at page {page}")
                        text = await resp.text()
                        print(f"Response: {text[:200]}")
                        break

            except Exception as e:
                print(f"\n❌ Exception on page {page}: {e}")
                break

    # Save results
    with open(output_file, 'w') as f:
        json.dump(all_files, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Scraping Complete!")
    print(f"{'='*60}")
    print(f"Total files found: {len(all_files)}")
    print(f"Saved to: {output_file}")
    print(f"\nFirst 5 files:")
    for i, file in enumerate(all_files[:5], 1):
        print(f"  {i}. {file['filename']} from {file['repo']}")

    return all_files

if __name__ == "__main__":
    asyncio.run(scrape_blend_files())
