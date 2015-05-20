from django.contrib.auth.models import User
from django.test import TestCase

from pubsubpull.models import Request, UpdateLog

from slumber_examples.models import Pizza


class TestMiddleware(TestCase):
    def setUp(self):
        self.user = User(username='test', is_superuser=True)
        self.user.set_password('password')
        self.user.save()

    def test_request_is_recorded(self):
        response = self.client.get("/slumber/")
        self.assertEqual(UpdateLog.objects.all().count(), 0)
        self.assertEqual(Request.objects.all().count(), 1)
        request = Request.objects.all()[0]
        self.assertIsNone(request.user)
        self.assertEquals(request.method, "GET")
        self.assertEquals(request.path, "/slumber/")
        self.assertIsNotNone(request.duration)
        self.assertEquals(request.status, response.status_code)

    def test_authenticated_request(self):
        self.client.login(username='test', password='password')
        response = self.client.get("/slumber/")
        self.assertEqual(UpdateLog.objects.all().count(), 0)
        self.assertEqual(Request.objects.all().count(), 1)
        request = Request.objects.all()[0]
        self.assertEquals(self.user, request.user)
