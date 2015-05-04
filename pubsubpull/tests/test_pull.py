from django.test import TestCase

from pubsubpull.api import pull


def job():
    pass


class TestPullStarts(TestCase):
    def test_pull(self):
        pull('slumber://test/Instance/', 'pubsubpull.tests.test_pull.job')
