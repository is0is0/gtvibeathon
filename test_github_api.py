#!/usr/bin/env python3
"""Test GitHub API to see if we can find .blend files."""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_github_search():
    """Test if GitHub API can find .blend files."""
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("❌ No GITHUB_TOKEN found!")
        return

    print(f"✅ Token loaded: {token[:15]}...")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Try different search strategies
    searches = [
        # Repository search (more reliable than code search)
        "https://api.github.com/search/repositories?q=blender+language:Blender&per_page=10",
        "https://api.github.com/search/repositories?q=.blend+extension:blend&per_page=10",
        "https://api.github.com/search/repositories?q=blender+3d&per_page=10",

        # Code search
        "https://api.github.com/search/code?q=extension:blend&per_page=10",
    ]

    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(searches, 1):
            print(f"\n{'='*60}")
            print(f"Search {i}: {url}")
            print('='*60)

            try:
                async with session.get(url, headers=headers) as resp:
                    print(f"Status: {resp.status}")

                    if resp.status == 200:
                        data = await resp.json()
                        total = data.get('total_count', 0)
                        items = data.get('items', [])

                        print(f"Total results: {total}")
                        print(f"Returned items: {len(items)}")

                        if items:
                            print("\nFirst 3 results:")
                            for idx, item in enumerate(items[:3], 1):
                                if 'name' in item:  # Repository
                                    print(f"  {idx}. Repo: {item.get('full_name')} - {item.get('description', 'No desc')[:50]}")
                                elif 'path' in item:  # Code file
                                    print(f"  {idx}. File: {item.get('path')} in {item.get('repository', {}).get('full_name', 'unknown')}")
                        else:
                            print("  No items returned")

                    elif resp.status == 403:
                        print(f"❌ Rate limited or forbidden")
                        text = await resp.text()
                        print(f"Response: {text[:200]}")

                    else:
                        print(f"❌ Error: {resp.status}")
                        text = await resp.text()
                        print(f"Response: {text[:200]}")

            except Exception as e:
                print(f"❌ Exception: {e}")

            await asyncio.sleep(2)  # Rate limit protection

if __name__ == "__main__":
    asyncio.run(test_github_search())
