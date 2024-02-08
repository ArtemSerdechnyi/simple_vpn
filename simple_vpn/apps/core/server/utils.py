from aiohttp import web, ClientResponse


def convert_dict_keys_to_lowercase(d: dict) -> dict:
    if isinstance(d, dict):
        return {key.lower(): convert_dict_keys_to_lowercase(value) for key, value in d.items()}
    else:
        return d


def capitalize_headers_name(d: dict[str]) -> dict:
    if isinstance(d, dict):
        return {'-'.join(map(lambda x: x.capitalize(), key.split('-'))): value
                for key, value in d.items()}
    else:
        return d
