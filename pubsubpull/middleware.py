"""
    Middleware for pubsubpull.
"""
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from django.db import connection

from pubsubpull.models import Request


class RequestUser:
    """
        Records the current user in the session
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        log = Request.objects.create(user=user, method=request.method,
            path=request.path)
        connection.cursor().execute("SET LOCAL pubsubpull.request_id=%s;" % log.id)
        request.pubsubpull = dict(log=log)


class RequestTracker(RequestUser):
    """
        Used to record the result of requests.
    """
    def process_response(self, request, response):
        if getattr(request, 'pubsubpull' , None):
            log = request.pubsubpull['log']
            log.duration = (timezone.now() - log.started).seconds
            log.status = response.status_code
            log.save()
        return response
