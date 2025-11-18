import nest_asyncio, threading, time, random, requests, os, statistics, asyncio

def is_ready(url: str | None) -> bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")


