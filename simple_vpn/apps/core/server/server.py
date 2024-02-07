from typing import Callable

from django.conf import settings
import aiohttp
from aiohttp import web

from common_utils.url_utils import get_query_from_url, add_GET_query_params_to_url
from .utils import capitalize_headers_name


class ProxyServer:
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port

    @staticmethod
    def get_necessary_headers(request: web.Request):
        headers = {}
        irh = capitalize_headers_name(settings.INHERITED_REQUEST_HEADERS)
        request_headers = capitalize_headers_name(dict(request.headers))
        for name, value in irh.items():
            if name not in request_headers:
                continue
            if value:
                if isinstance(value, str):
                    headers[name] = value
                elif isinstance(value, Callable):
                    headers[name] = value(request)
            else:
                headers[name] = request_headers[name]
        return headers

    async def static_request(self, request: web.Request):
        url = request.match_info.get("url")
        query = get_query_from_url(str(request.url))
        url_with_parameters = add_GET_query_params_to_url(url, query)
        if not url:
            return web.Response(text='Missing "url" parameter', status=400)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url_with_parameters,
                        headers=self.get_necessary_headers(request)
                ) as response:
                    body = await response.read()
                    status = response.status

                if status != 200:
                    async with session.get(
                            url_with_parameters,
                    ) as response:
                        body = await response.read()
                        status = response.status


        except aiohttp.ClientError as ce:
            return web.Response(status=500, text=f"ClientError: {ce}")
        else:
            return web.Response(
                body=body,
                status=status,
                content_type="text/html",
            )

    def run(self):
        app = web.Application()
        app.add_routes((
            web.RouteDef('GET', '/request/{params:.*}/{url:https?://.*}', self.static_request, {}),
        ))
        web.run_app(app, host=self.host, port=self.port)
