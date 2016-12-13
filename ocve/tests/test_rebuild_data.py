__author__ = 'elliotthall'
# -*- coding: utf-8 -*-

from django.test import TestCase

#A suite of tests to ensure the rebuild data functions for serializing the database
#to the JSON files used by Pourover in the main UI perform as expected

class TestRebuildData(TestCase):

    def setUp(self):
        #OCVE Sources
        #CFEO Sources (Posthumous)
        #Catalogue AC codes?
        pass


    def test_serializeOCVESourceJson(self):
        pass

    def test_serializeCFEOSourceJson(self):
        pass

    def test_serializeSourceComponents(self):
        pass

    def test_serializePages(self):
        pass

    def test_serializeAcCodeConnector(self):
        pass

    def test_generateThumbnail(self):
        #Get test page
        #Generate thumbnail
        #Load it back to verify it's there and nonzero
        pass
