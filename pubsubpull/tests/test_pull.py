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

    def test_pull_up_two(self):
        pizzas = []
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 1))
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 2))
        pull_up('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.tests.test_pull.job').count(), 2)
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pullup_monitor', executed=None).count(), 1)
        return pizzas

    def test_pull_up_two_then_two(self):
        pizzas = self.test_pull_up_two()
        print("*** -- dropping scheduled time on jobs to force execution")
        Job.objects.exclude(scheduled=None).update(scheduled=None)
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 3))
        pizzas.append(Pizza.objects.create(name="Pizza %s" % 4))
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pullup_monitor', executed=None).count(), 1)
        self.check_pizzas(pizzas)

    def test_pull_down_eleven(self):
        pizzas = []
        for p in range(1, 12):
            pizzas.append(Pizza.objects.create(name="Pizza %s" % p))
        pull_down('slumber://pizza/slumber_examples/Pizza/', 'pubsubpull.tests.test_pull.job')
        self.assertEquals(Job.objects.count(), 1)
        management.call_command('flush_queue')
        self.assertEquals(Job.objects.filter(name='pubsubpull.async.pulldown_monitor').count(), 3)
        self.assertEquals(Job.objects.filter(name='pubsubpull.tests.test_pull.job').count(), 11)
        self.check_pizzas(pizzas)

