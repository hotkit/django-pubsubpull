from django.test import TestCase

from pubsubpull.models import Request, UpdateLog


class TestMiddleware(TestCase):
    def test_request_is_recorded(self):
        response = self.client.get("/slumber/")
        self.assertEqual(UpdateLog.objects.all().count(), 0)
        self.assertEqual(Request.objects.all().count(), 1)
        request = Request.objects.all()[0]
        self.assertIsNone(request.user)
        self.assertEquals(request.method, "GET")
        self.assertEquals(request.path, "/slumber/")
        self.assertIsNotNone(request.duration)
