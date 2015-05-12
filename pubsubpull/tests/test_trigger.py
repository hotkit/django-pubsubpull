from django.core.exceptions import ValidationError
from django.test import TestCase

from pubsubpull.api import add_trigger_function, change_detect
from pubsubpull.models import UpdateLog

from slumber_examples.models import Pizza


class TestTrigger(TestCase):
    def setUp(self):
        add_trigger_function()

    def test_cannot_save(self):
        with self.assertRaises(ValidationError):
            UpdateLog.objects.create()

    def test_insert_is_recorded(self):
        change_detect(Pizza)
        p1 = Pizza.objects.create(name="P1")
        self.assertEqual(UpdateLog.objects.count(), 1)
        log = UpdateLog.objects.all()[0]
        self.assertEqual(log.table, 'slumber_examples_pizza')
        self.assertIsNone(log.old)
        print type(log.new), log.new, repr(log.new)
        self.assertEqual(log.new, dict(id=p1.id, name="P1", exclusive_to_id=None,
            for_sale=False, max_extra_toppings=None))
