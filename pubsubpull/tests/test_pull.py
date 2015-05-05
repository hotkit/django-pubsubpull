from async.models import Job

from django.core import management
from django.test import TestCase

from pubsubpull.api import pull
from slumber_examples.models import Pizza


def job():
    pass


class TestPullStarts(TestCase):
    def test_empty_pull(self):
        pull('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 2)

    def test_pull_one(self):
        pizza = Pizza.objects.create(name="Vegetarian")
        pull('slumber://slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 3)
