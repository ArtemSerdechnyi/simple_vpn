from urllib.parse import urlparse, urljoin


def get_path_from_url(url: str) -> str:
    return urlparse(url).path


def get_query_from_url(url: str) -> str:
    return urlparse(url).query


def get_netloc_from_url(url: str) -> str:
    return urlparse(url).netloc


def get_home_site_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def add_GET_query_params_to_url(url: str, params: dict | str) -> str:
    if params:
        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith("?"):
            url += '?'

        if isinstance(params, str):
            url += params
        elif isinstance(params, dict):
            for key, value in params.items():
                url += key + '=' + value + '&'
            url = url[:-1]
    return url


def remove_GET_query_params_from_url(url: str) -> str:
    query = get_query_from_url(url)
    if query:
        url = url.replace(query, '')
        if url.endswith("?"):
            url = url[:-1]
    return url


def merge_url_path_query(url, path, query=None):
    url = get_home_site_url(url)
    path = get_path_from_url(path)
    url_with_path = urljoin(url, path)
    if query:
        query = get_query_from_url(query)
        result_url = add_GET_query_params_to_url(url_with_path, query)
        return result_url
    return url_with_path
