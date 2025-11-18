import nest_asyncio, threading, time, random, os, statistics, asyncio
from typing import Optional

def is_ready(url: Optional[str]) -> bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")


