"""
    Middleware for pubsubpull.
"""


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
