from async.models import Job

from django.core import management
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from pubsubpull.api import pull
from slumber import data_link
from slumber.connector.ua import for_user
from slumber_examples.models import Pizza


def job(url):
    TestPullStarts.URLS.add(url)


class TestPullStarts(TestCase):
    def setUp(self):
        self.service = User.objects.create(username=settings.SLUMBER_SERVICE,
            is_active=True, is_staff=True, is_superuser=True,
            password=settings.SECRET_KEY)
        TestPullStarts.URLS = set()

    def test_empty_pull(self):
        pull('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 2)

    def test_pull_one(self):
        pizza = Pizza.objects.create(name="Vegetarian")
        pull('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 3)
        self.assertIn(data_link(pizza), self.URLS)
