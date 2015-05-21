import json

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from pubsubpull.api import add_trigger_function, change_detect
from pubsubpull.models import Request, UpdateLog

from slumber_examples.models import Pizza


class TestTrigger(TestCase):
    def setUp(self):
        add_trigger_function()
        self.user = User(username='test', is_superuser=True)
        self.user.set_password('password')
        self.user.save()
        self.client.login(username='test', password='password')

    def test_cannot_save(self):
        with self.assertRaises(ValidationError):
            UpdateLog.objects.create()

    def test_insert_is_recorded(self):
        change_detect(Pizza)
        p1 = Pizza.objects.create(name="P1")
        self.assertEqual(UpdateLog.objects.count(), 1)
        log = UpdateLog.objects.all()[0]
        self.assertEqual(log.table, 'slumber_examples_pizza')
        self.assertIsNone(log.request)
        self.assertIsNone(log.old)
        print type(log.new), log.new, repr(log.new)
        self.assertEqual(log.new, dict(id=p1.id, name="P1", exclusive_to_id=None,
            for_sale=False, max_extra_toppings=None))

    def test_update_view_gives_JSON(self):
        change_detect(Pizza)
        p1 = Pizza.objects.create(name="P3")
        self.assertEqual(UpdateLog.objects.count(), 1)
        log = UpdateLog.objects.all()[0]
        response = self.client.get('/slumber/pizza/pubsubpull/UpdateLog/data/%s/' % log.id)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data["fields"]["new"]["data"], log.new)
