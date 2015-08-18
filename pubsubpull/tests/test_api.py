import json

from async.models import Job
from django.conf import settings
from django.contrib.auth.models import User
from django.core import management
from django.test import TestCase
from mock import patch
from slumber.scheme import from_slumber_scheme

from slumber_examples.models import Pizza

from pubsubpull.api import monitor_model, monitor_service, async_monitor, change_detect, _get_base_url, \
    _get_data_from_slumber
from pubsubpull.models import ChangeSubscription


def callback_test(param1='Ruby'):
    pass


class TestApiMonitor(TestCase):
    callback = 'pubsubpull.tests.test_api.callback_test'
    callback_kwargs = {'param1': 'Title'}
    model_url = 'slumber://pizza/slumber_examples/Pizza/'
    table = 'slumber_examples_pizza'
    update_log_model_url = 'slumber://pizza/pubsubpull/UpdateLog/'

    def setUp(self):
        User.objects.create(username=settings.SLUMBER_SERVICE,
                            is_active=True, is_staff=True, is_superuser=True,
                            password=settings.SECRET_KEY)
        change_detect(Pizza)

    @patch('pubsubpull.api.pull_down')
    @patch(callback)
    def test_call_async_monitor(self, mock_callback_test, mock_pull_down):
        self.client.login(username='test', password='password')
        monitor_model(update_log_model_url=self.update_log_model_url,
                      model_url=self.model_url,
                      table=self.table,
                      callback=self.callback,
                      callback_kwargs=self.callback_kwargs)
        pizza = Pizza.objects.create(name="P1")
        pizza_instance_url = from_slumber_scheme('slumber://pizza/slumber_examples/Pizza/data/{}/'.format(pizza.pk))
        async_monitor(update_log_url='slumber://pizza/pubsubpull/UpdateLog/data/1',
                      update_log_model_url=self.update_log_model_url)
        management.call_command('flush_queue')
        # callback_test must be called
        mock_callback_test.assert_called_with(pizza_instance_url,
                                              **self.callback_kwargs)

    @patch(callback)
    def test_call_monitor_model(self, mock_callback_test):
        self.client.login(username='test', password='password')
        monitor_model(update_log_model_url=self.update_log_model_url,
                      model_url=self.model_url,
                      table=self.table,
                      callback=self.callback,
                      callback_kwargs=self.callback_kwargs)
        # it should create a new ChangeSubscription object
        ss = ChangeSubscription.objects.all()[0]
        self.assertEqual(ss.update_log_model_url, self.update_log_model_url)
        self.assertEqual(ss.table, self.table)
        self.assertEqual(ss.callback, self.callback)
        self.assertDictEqual(json.loads(ss.callback_kwargs),
                             self.callback_kwargs)
        # it should create a job in django-async
        job = Job.objects.all()[0]
        self.assertEqual(job.name, 'pubsubpull.async.pull_monitor')
        self.assertEqual(json.loads(job.args), [self.model_url, self.callback])
        self.assertDictEqual(json.loads(job.kwargs), dict(delay=0, callback_kwargs=dict(param1="Title")))
        # callback_test should be called because there is a pizza
        pizza = Pizza.objects.create(name="P1")
        pizza_instance_url = from_slumber_scheme('slumber://pizza/slumber_examples/Pizza/data/{}/'.format(pizza.pk))
        management.call_command('flush_queue')
        mock_callback_test.assert_called_with(pizza_instance_url,
                                              **self.callback_kwargs)

    @patch('pubsubpull.api.pull_up')
    def test_call_monitor_service(self, pull_up):
        expected_callback_kwargs = {'update_log_model_url': self.update_log_model_url}
        monitor_service(self.update_log_model_url)
        # it should call pull_up
        pull_up.assert_called_with(
            self.update_log_model_url,
            'pubsubpull.api.async_monitor',
            callback_kwargs=expected_callback_kwargs)


class TestUtilFunctions(TestCase):

    def test_get_base_url(self):
        actual = _get_base_url('http://www.cwi.nl:80/%7Eguido/Python.html')
        expected = 'http://www.cwi.nl:80'
        self.assertEqual(actual, expected)

    @patch('pubsubpull.api.get')
    def test_get_data_from_slumber(self, mock_get):
        source_url = 'slumber://pizza/slumber_examples/Pizza/'
        mock_get.return_value = None, 'response'
        actual = _get_data_from_slumber(source_url)
        mock_get.assert_called_with(from_slumber_scheme(source_url))
        self.assertEqual(actual, 'response')
