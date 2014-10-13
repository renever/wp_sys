from django.db import models
from django.utils import timezone

# custom model manager
class PublishedManager(models.Manager):

    use_for_related_fields = True

    def published(self, **kwargs):
        return self.filter(pub_date_lte=timezone.now(), **kwargs)

class FlavorReview(models.Model):
    review = models.CharField(max_length=255)
    pub_date = models.DataTimeField()

    objects = PublishedManager()
#page:112
DATABASES = {
        'default': {
            #...
            'ATOMIC_REQUESTS': True,
            },
        }

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Flavor

@transaction.non_atomic_requests
def posting_flavor_status(requests, pk, status):
    flavor = get_object_or_404(flavor, pk=pk)

    #This will execute in autocommit mode (Django's default).
    flavor.latest_status_change_attempt = timezone.now()
    flavor.save()

    with transaction.atomic():
        # This code executes inside a transaction.
        flavor.status = status
        flavor.latest_status_change_success = timezone.now()
        return HttpResponse("Hooray")

    # If the transaction fails,return the appropriate status
    return HttpResponse("Sadness",status_code=400)




