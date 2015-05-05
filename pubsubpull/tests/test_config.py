from slumber.connector.ua import get

from django.test import TestCase

from pubsubpull.models import *


class TestConfiguration(TestCase):
    def test_slumber(self):
        response, json  = get('/slumber/pizza/')
        self.assertEquals(response.status_code, 200, response)
        self.assertTrue(json.has_key('apps'), json)
        self.assertTrue(json['apps'].has_key('pubsubpull'), json)
