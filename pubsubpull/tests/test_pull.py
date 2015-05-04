from async.models import Job

from django.test import TestCase

from pubsubpull.api import pull


def job():
    pass


class TestPullStarts(TestCase):
    def test_pull(self):
        pull('slumber://test/Instance/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
