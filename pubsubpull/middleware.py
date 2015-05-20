"""
    Middleware for pubsubpull.
"""
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from pubsubpull.models import Request


class RequestTracker:
    """
        Used to record requests and tie them in to database changes.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        log = Request.objects.create(user=user,
            method=request.method, path=request.path)
        request.pubsubpull = dict(log=log)

    def process_response(self, request, response):
        if getattr(request, 'pubsubpull' , None):
            log = request.pubsubpull['log']
            log.duration = (timezone.now() - log.started).seconds
            log.status = response.status_code
            log.save()
        return response
