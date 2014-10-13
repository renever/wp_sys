from os.path import join, abspath, dirname
here = lambda *dirs: join(abspath(dirname(__file__)), *dirs)
BASE_DIR = here("..", "..")
print BASE_DIR
root = lambda *dirs: join(abspath(BASE_DIR), *dirs)

MEDIA_ROOT = root("media")
print MEDIA_ROOT
STATIC_ROOT = root("collected_static")

from django.db import models
from django.utils import timezone


class PublishedManager(models.Manager):

    use_for_related_fields = True

    def published(self, **kwargs):
        return self.filter(pub_date_lte=timezone.now(), **kwargs)

class FlavorReview(models.Model):
    review = models.CharField(max_length=255)
    pub_date = models.DataTimeField()

    objects = PublishedManager()
