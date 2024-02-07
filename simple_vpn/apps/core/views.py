from bs4 import BeautifulSoup

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.conf import settings

from .utils import (
    send_request,
    RequestParameters,
    process_soup,
)


def index(request: WSGIRequest):
    return render(request, 'core/index.html')


class Pars(View):

    @staticmethod
    async def post(request: WSGIRequest, **kwargs):
        rp = RequestParameters(request)
        tags = settings.CHANGING_TAGS
        attrs = settings.CHANGING_ATTRIBUTES

        text, status = await send_request(rp)
        if status != 200:
            return HttpResponse('Oops!', status=status, content_type='text/html')

        soup = BeautifulSoup(text, "html.parser")
        soup = process_soup(soup, rp, tags, attrs)
        text = str(soup)
        return HttpResponse(text, status=status, content_type='text/html')
