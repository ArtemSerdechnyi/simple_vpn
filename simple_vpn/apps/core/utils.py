import sys
from typing import Iterable
from urllib.parse import urlparse, urljoin

from aiohttp import ClientResponse
from multidict import CIMultiDict

import aiohttp
import bs4
from bs4 import Tag
from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict, Http404

from django.conf import settings

from common_utils.url_utils import get_path_from_url, get_query_from_url, add_GET_query_params_to_url, \
    remove_GET_query_params_from_url, get_home_site_url, get_netloc_from_url, merge_url_path_query

from ..users.models import Site, Request, User


class RequestParameters:

    def __init__(self, request: WSGIRequest):
        self.request = request
        additional_param: QueryDict = request.POST
        self.site_pk = additional_param.get('site.pk')
        self.my_site_netloc = urlparse(request.build_absolute_uri()).netloc
        self.name = additional_param.get('site.name')
        self.target_url = additional_param.get('site.origin_url')
        self.original_netloc = additional_param.get('site.netloc')
        self.original_path = additional_param.get('site.path', '')
        self.original_query = additional_param.get('site.query', '')
        self.home_page_url = get_home_site_url(self.target_url)
        self.headers = request.headers


def filter_non_empty_headers(headers: CIMultiDict) -> CIMultiDict:
    return CIMultiDict([(key, value) for key, value in headers.items() if value.strip()])


def get_request_size(url, headers):
    """
    Calculate the size of the HTTP GET request in bytes.
    """
    request_size = sys.getsizeof(url.encode('utf-8'))
    for header_name, header_value in headers.items():
        request_size += sys.getsizeof(header_name.encode('utf-8')) + sys.getsizeof(header_value.encode('utf-8'))
    return request_size


async def get_response_size(response: ClientResponse):
    """
    Calculate the size of the HTTP response in bytes.
    """
    response_size = len(await response.read())
    return response_size


async def send_request(rp: RequestParameters) -> tuple[str, int, int, int]:
    """
    Send an HTTP GET request and return the response data along with request and response sizes.
    """
    headers = rp.headers
    name = rp.name
    target_url = rp.target_url
    headers = filter_non_empty_headers(headers)
    url = get_aiohttp_url(name, target_url)

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            text = await response.text()
            status = response.status
            requests_size = get_request_size(url, headers)
            response_size = await get_response_size(response)
    return text, status, requests_size, response_size


def get_aiohttp_url(name, target_url):
    host = settings.PROXY_SERVER_HOST
    port = settings.PROXY_SERVER_PORT
    url = f'http://{host}:{port}/request/{name}/{target_url}'
    return url


def refactor_absolute_origin_url_to_mysite_absolute_url(rp: RequestParameters, original_tag_url):
    scheme = rp.request.scheme
    my_site_netloc = rp.my_site_netloc.strip('/')
    name = rp.name.strip('/')
    original_netloc = get_netloc_from_url(original_tag_url).strip('/')
    original_path = get_path_from_url(original_tag_url).strip('/')
    original_query = get_query_from_url(original_tag_url)
    url = f'{scheme}://{my_site_netloc}/{name}/{original_netloc}/{original_path}/'

    if not url.endswith('/'):
        url += '/'
    if original_query:
        url = add_GET_query_params_to_url(url, original_query)
    return url


def add_base_tag_to_soup(soup: bs4.BeautifulSoup, rp: RequestParameters):
    netloc = rp.original_netloc
    base_tag = soup.find('base')
    if not base_tag:
        base_tag = soup.new_tag('base')
        base_tag['href'] = f"//{netloc}/"
        head_tag = soup.find('head')
        if head_tag:
            head_tag.insert(0, base_tag)
        return soup


def update_relative_link_to_full(relative_link, target_url: str):
    path = get_path_from_url(relative_link)
    if path:
        query = get_query_from_url(relative_link)
        target_url_path = get_path_from_url(target_url)
        url = target_url.replace(target_url_path, path)
        url_with_query = add_GET_query_params_to_url(url, query)
        return url_with_query
    return path


def get_action_for_form(url: str, request) -> str:
    query = get_query_from_url(url)
    if query:
        pass
    return request.build_absolute_uri().replace(request.path, urlparse(url).path)


def wrap_tag_in_post_form(
        tag: bs4.Tag,
        url: str,
        original_full_url_in_tag,
        soup: bs4.BeautifulSoup,
        rp: RequestParameters,
) -> bs4.Tag:
    form_tag = soup.new_tag("form", method="post", action=remove_GET_query_params_from_url(url))
    for key, value in rp.request.POST.items():
        if key == 'site.path':
            value = get_path_from_url(original_full_url_in_tag)
        elif key == 'site.origin_url':
            value = original_full_url_in_tag
            # value = urljoin(value, original_path_in_tag_url)
        elif key == 'site.query':
            value = get_query_from_url(original_full_url_in_tag)
            # value = get_query_from_url(url)
        input_tag = soup.new_tag("input", type="hidden", attrs={
            'name': key,
            'value': value,
        })
        form_tag.append(input_tag)
    tag["href"] = "#"
    tag["onclick"] = "submitClosestForm(this); return false;"
    tag.wrap(form_tag)
    return tag


def add_js_to_end_of_page(soup: bs4.BeautifulSoup, js_src: str):
    script_tag = soup.new_tag('script', src=js_src)
    body_tag = soup.find('body')
    if body_tag:
        body_tag.append(script_tag)
    else:
        soup.html.append(script_tag)
    return soup


def find_all_tags_with_some_attr(
        soup: bs4.BeautifulSoup,
        tags: Iterable[str],
        attrs: Iterable[str]
) -> tuple[Tag, str]:
    for tag in soup.find_all(tags):
        for attr in attrs:
            if tag.has_attr(attr):
                yield tag, attr


def filter_tag(tag: Tag, attr, original_netloc) -> Tag | None:
    url = tag[attr]
    netloc = get_netloc_from_url(url)
    if netloc:
        if netloc == original_netloc:
            return tag
    else:
        return tag


def is_relative(url: str) -> bool:
    if get_netloc_from_url(url):
        return False
    else:
        return True


def refactor_relative_url_to_absolute_origin_url():
    pass


def process_soup(
        soup: bs4.BeautifulSoup,
        rp: RequestParameters,
        tags: Iterable[str],
        attrs: Iterable[str],
) -> bs4.BeautifulSoup:
    """
    Process the BeautifulSoup object by adding a base tag,
    filter tags with attributes based on tags and attrs,
    update attribute in tag,
    wrapping them in forms,
    add <script> '/static/js/submitClosestForm.js' to the end of the page.
    """

    soup = add_base_tag_to_soup(soup, rp)

    for tag, attr in find_all_tags_with_some_attr(soup, tags, attrs):
        tag = filter_tag(tag, attr, rp.original_netloc)
        if not tag:
            continue
        if get_path_from_url(tag[attr]) != "/":
            pass

        original_full_url_in_tag = merge_url_path_query(
            rp.home_page_url,
            tag[attr],
            tag[attr],
        )

        tag[attr] = refactor_absolute_origin_url_to_mysite_absolute_url(rp, original_full_url_in_tag)

        # wrap tag in form
        form_tag = wrap_tag_in_post_form(tag, tag[attr], original_full_url_in_tag, soup, rp)
        # replace tag to wrapped tag
        tag.replace_with(form_tag)

    submit_closest_form_path = rp.request.build_absolute_uri().replace(rp.request.path,
                                                                       "/static/js/submitClosestForm.js")
    soup = add_js_to_end_of_page(soup, submit_closest_form_path)
    return soup


async def get_site(rp: RequestParameters, user: User) -> Site:
    """
    Retrieves a site object asynchronously based on the provided RequestParameters and User.
    """
    try:
        site = await Site.objects.aget(
            pk=rp.site_pk,
            user=user,
        )
    except Site.DoesNotExist:
        raise Http404("Site does not exist or you don't have permission to access it.")
    return site


async def create_request(rp: RequestParameters, user: User, data_sent, data_received) -> Request:
    """
    Creates a new request asynchronously and returns the associated Request object.
    """
    return await Request.objects.acreate(
        user=user,
        site=await get_site(rp, user),
        data_sent=data_sent,
        data_received=data_received,
    )
