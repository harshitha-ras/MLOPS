cache_dict = {}

def get_cached(prompt: str):
    return cache_dict.get(prompt)

def set_cached(prompt: str, response: str):
    cache_dict[prompt] = response
