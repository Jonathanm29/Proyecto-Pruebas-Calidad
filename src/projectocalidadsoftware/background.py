import nest_asyncio, threading, time, random, os, statistics, asyncio
from typing import Optional

def ants_needed(damage: int, dpa: int) -> int:
    import math
    return max(1, math.ceil(damage / dpa))

def is_ready(url: Optional[str]) -> bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")


