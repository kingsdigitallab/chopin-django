__author__ = 'elliotthall'
# -*- coding: utf-8 -*-

from django.test import TestCase
from ocve.models import *
from ocve.uitools import *
from ocve.uiviews import *

#A suite of tests to ensure the rebuild data functions for serializing the database
#to the JSON files used by Pourover in the main UI perform as expected

class TestRebuildData(TestCase):

    def setUp(self):
        pass
