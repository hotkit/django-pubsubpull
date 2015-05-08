from django.core.exceptions import ValidationError
from django.test import TestCase

from pubsubpull.models import UpdateLog


class TestTrigger(TestCase):
    def test_cannot_save(self):
        with self.assertRaises(ValidationError):
            UpdateLog.objects.create()

    def test_insert_is_recorded(self):
        pass
