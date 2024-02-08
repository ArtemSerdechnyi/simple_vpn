from bs4 import BeautifulSoup

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views import View
from django.conf import settings

from .utils import (
    send_request,
    RequestParameters,
    process_soup, create_request,
)

from ..users.models import User


def index(request: WSGIRequest):
    return render(request, 'core/index.html')


class Pars(View):

    async def post(self, request: WSGIRequest, **kwargs):
        user: User = await request.auser()
        if not user.is_authenticated:
            return HttpResponse('User authenticated error!', status=401, content_type='text/html')

        rp = RequestParameters(request)
        tags = settings.CHANGING_TAGS
        attrs = settings.CHANGING_ATTRIBUTES

        text, status, requests_size, response_size = await send_request(rp)
        db_request = await create_request(rp, user, requests_size, response_size)

        if status != 200:
            return HttpResponse('Oops!', status=status, content_type='text/html')

        soup = BeautifulSoup(text, "html.parser")
        soup = process_soup(soup, rp, tags, attrs)
        text = str(soup)
        return HttpResponse(text, status=status, content_type='text/html')
