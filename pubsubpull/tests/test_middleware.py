from django.contrib.auth.models import User
from django.test import TestCase

from pubsubpull.api import add_trigger_function, change_detect
from pubsubpull.models import Request, UpdateLog

from slumber_examples.models import Pizza


class TestMiddleware(TestCase):
    def setUp(self):
        add_trigger_function()
        change_detect(Pizza)
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

    def test_update_attached_to_request(self):
        self.client.login(username='test', password='password')
        self.client.post(
            '/slumber/pizza/slumber_examples/Pizza/create/',
            dict(name="p2"))
        self.assertEqual(UpdateLog.objects.all().count(), 1)
        self.assertEqual(Request.objects.all().count(), 1)
        pizza = Pizza.objects.all()[0]
        self.assertEquals(pizza.name, 'p2')
        request = Request.objects.all()[0]
        self.assertEquals(request.changes.all().count(), 1)
