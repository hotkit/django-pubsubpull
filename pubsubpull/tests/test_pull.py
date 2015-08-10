import json
from async.models import Job

from django.core import management
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from pubsubpull.api import pull, pull_up, pull_down
from slumber import data_link
from slumber.connector.ua import for_user
from slumber.scheme import from_slumber_scheme
from slumber_examples.models import Pizza
from urlparse import urljoin


def job(url):
    assert url not in TestPullStarts.URLS
    TestPullStarts.URLS.add(url)


class TestPullStarts(TestCase):
    def setUp(self):
        self.service = User.objects.create(username=settings.SLUMBER_SERVICE,
            is_active=True, is_staff=True, is_superuser=True,
            password=settings.SECRET_KEY)
        TestPullStarts.URLS = set()

    def check_pizzas(self, pizzas):
        base = from_slumber_scheme('slumber://pizza/slumber_examples/Pizza/')
        urls = [urljoin(base, data_link(p)) for p in pizzas]
        self.assertEquals(set(urls), self.URLS)

    def print_jobs(self, jobs=None):
        if not jobs:
            jobs = Job.objects.all()
        print("*** %s jobs ***" % jobs.count())
        for j in jobs.order_by('pk'):
            print(j.id, j, j.executed, j.scheduled)

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
        self.assertEquals(Job.objects.count(), 4)
        self.check_pizzas([pizza])

    def test_pull_eleven(self):
        pizzas = []
        for p in range(1, 12):
            pizzas.append(Pizza.objects.create(name="Pizza %s" % p))
        pull('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 15)
        self.check_pizzas(pizzas)
        return pizzas

    def test_pull_eleven_then_eleven(self):
        pizzas = self.test_pull_eleven()
        for p in range(12, 23):
            pizzas.append(Pizza.objects.create(name="Pizza %s" % p))
        print("*** -- dropping scheduled time on jobs to force execution")
        Job.objects.exclude(scheduled=None).update(scheduled=None)
        management.call_command('flush_queue')
        self.print_jobs()
        self.print_jobs(Job.objects.exclude(scheduled=None))
        self.print_jobs(Job.objects.filter(name='pubsubpull.async.pull_monitor'))
        self.assertEquals(Job.objects.count(), 28)
        self.check_pizzas(pizzas)
        return pizzas

    def test_pull_eleven_then_eleven_then_one(self):
        pizzas = self.test_pull_eleven_then_eleven()
        pizzas.append(Pizza.objects.create(name="Four cheeses"))
        print("*** -- dropping scheduled time on jobs to force execution")
        Job.objects.exclude(scheduled=None).update(scheduled=None)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 30)

    def test_pull_priority(self):
        pizza = Pizza.objects.create(name="Vegetarian")
        pull('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job',
            pull_priority=7, job_priority=6)
        self.assertEquals(Job.objects.filter(priority=7).count(), 1, Job.objects.all())
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(priority=6).count(), 1, Job.objects.all())
        self.assertEquals(Job.objects.filter(priority=7).count(), 3, Job.objects.all())

    def test_set_pullup_and_pulldown_two(self):
        pizzas = []
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 1))
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 2))
        pull_down('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job', delay=None)
        pull_up('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 2)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pull_monitor', executed=None).count(), 1)
        self.check_pizzas(pizzas)
        return pizzas

    def test_set_pullup_and_pulldown_two_then_pullup_two(self):
        pizzas = self.test_set_pullup_and_pulldown_two()
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 3))
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 4))
        print("*** -- dropping scheduled time on jobs to force execution")
        Job.objects.exclude(scheduled=None).update(scheduled=None)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pull_monitor', executed=None).count(), 1)
        self.check_pizzas(pizzas)

    def test_pull_down_eleven(self):
        pizzas = []
        for p in range(1, 12):
            pizzas.append(Pizza.objects.create(name="Pizza %s" % p))
        pull_down('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pull_monitor').count(), 3)
        self.assertEquals(Job.objects.filter(name='pubsubpull.tests.test_pull.job').count(), 11)
        self.assertEquals(Job.objects.filter(executed=None).count(), 0)
        self.check_pizzas(pizzas)


def callback_with_kwargs(url, param1=1, param2='hello'):
    pass


class TestApiFunctions(TestCase):

    def setUp(self):
        self.service = User.objects.create(
            username=settings.SLUMBER_SERVICE,
            is_active=True, is_staff=True, is_superuser=True,
            password=settings.SECRET_KEY)

    def test_api_pull_add_new_job_with_callback_kwargs(self):
        callback_kwargs = dict(param1=10,
                               param2='python')
        pull('slumber://pizza/slumber_examples/Pizza/',
             'pubsubpull.tests.test_pull.callback_with_kwargs',
             callback_kwargs=callback_kwargs)
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 2)
        job_with_callback_kwargs = Job.objects.all()[1]
        self.assertDictEqual(callback_kwargs,
                             json.loads(job_with_callback_kwargs.kwargs)['callback_kwargs'])

    def test_pull_eleven(self):
        pizzas = [Pizza.objects.create(name="Pizza {}".format(i)) for i in range(1, 12)]
        callback_kwargs = dict(param1=10,
                               param2='python')
        pull('slumber://pizza/slumber_examples/Pizza/',
             'pubsubpull.tests.test_pull.callback_with_kwargs',
             callback_kwargs=callback_kwargs)
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.count(), 15)
        # every jobs added by pull should call callback with kwargs
        jobs_with_callback_kwargs = Job.objects.filter(name='pubsubpull.tests.test_pull.callback_with_kwargs')
        for _job in jobs_with_callback_kwargs:
            self.assertDictEqual(callback_kwargs,
                                 json.loads(_job.kwargs))

