import json
import hashlib

CACHE_FILE = "cache.json"

def _hash(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()

def get_cached(prompt):
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        return cache.get(_hash(prompt))
    except:
        return None

def set_cached(prompt, output):
    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    except:
        cache = {}
    cache[_hash(prompt)] = output
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
