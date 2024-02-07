from urllib.parse import urlparse

from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.utils.text import slugify
from django.db.models import Sum


class User(AbstractUser):
    age = models.IntegerField(null=True, blank=True)


class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sites")
    name = models.SlugField(max_length=100)
    origin_url = models.URLField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def netloc(self):
        return urlparse(self.origin_url).netloc.strip('/')

    @property
    def path(self):
        return urlparse(self.origin_url).path.strip('/')

    @property
    def query(self):
        return urlparse(self.origin_url).query

    def statistics(self):
        return {
            'total_requests': self.requests.count(),
            'total_data_sent': self.requests.aggregate(Sum('data_sent'))['data_sent__sum'] or 0,
            'total_data_received': self.requests.aggregate(Sum('data_received'))['data_received__sum'] or 0,
        }


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="requests")
    data_sent = models.BigIntegerField(default=0)
    data_received = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
