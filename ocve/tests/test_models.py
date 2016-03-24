# -*- coding: utf-8 -*-
__author__ = 'Elliott Hall'

from django.test import TestCase

from ocve.uiviews import *


class TestModels(TestCase):
    fixtures = ['test_models_fixtures.json']

    def setUp(self):
        pass
        # self.expected_highest_bar_number=186
        # self.expected_lowest_bar_number=183
        # self.expected_highest_bar=Bar.objects.get(barnumber=186)
        # self.expected_opus=Opus.objects.get(id=6611)
        # self.expected_accode="38–1-B&H"
        # self.expected_accodeobject=AcCode.objects.get(id=2887)
        # self.expected_sourcecomponents=SourceComponent.objects.all()
        # self.expected_sourceinformation=SourceInformation.objects.get(id=17522)
        # self.expected_primarypageimages=PageImage.objects.filter(versionnumber=1)
        # self.expected_pages=Page.objects.filter(sourcecomponent__source=self.expected_sources[0])
        # self.expected_firstbarregion=BarRegion.objects.get(id=269392)
        # self.default_sourcecomponent=SourceComponent.objects.get(id=36496)
        # self.expected_sourcecomponent_pages=Page.objects.filter(sourcecomponent=self.default_sourcecomponent)
        #
        # self.expected_instruments=Instrument.objects.get(id=1)

        # self.expected_page_primarypageimage=PageImage.objects.filter(page=self.default_page)
        # self.expected_workcomponent=WorkComponent.objects.get(id=9303)


    # Work
    def test_work_getSources(self):
        work=Work.objects.get(id=6337)
        self.assertEqual(1, work.getSources().count())
        first=work.getSources()[0]
        self.assertEqual(u"GFE: first impression (G)",first.label)

    #BarRegion
    def test_barregion_getHighestBarNumber(self):
        barregion=BarRegion.objects.get(id=269389)
        self.assertEqual(186,barregion.getHighestBarNumber())

    #todo: MAke multibar fixture
    def test_barregion_getLowestBarNumber(self):
        barregion=BarRegion.objects.get(id=269392)
        self.assertEqual(183,barregion.getLowestBarNumber())

    def test_barregion_getHighestBar(self):
        barregion=BarRegion.objects.get(id=269389)
        self.assertEqual(186,barregion.getHighestBar().barnumber)
    #
    # #Source
    #
    def test_source_getWork(self):
        source_gfe38=Source.objects.get(id=17890)
        self.assertNotEqual(None,source_gfe38.getWork())
        self.assertEqual(u"Ballade Op. 38",source_gfe38.getWork().label)


    #w.label+" "+self.label
    def test_source_getOpusLabel(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(u"Ballade Op. 38 GFE: first impression (G)",source.getOpusLabel())

    def test_source_getAcCode(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(u"38–1-B&H",source.getAcCode())


    def test_source_getAcCodeObject(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(u"38–1-B&H",source.getAcCodeObject().accode)


    def test_source_getSourceComponents(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(1,source.getSourceComponents().count())
        sc=source.getSourceComponents()[0]
        self.assertEqual(2,sc.orderno)


    def test_source_getSourceInformation(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(u"Ballade pour le Piano, Oeuvr. 38",source.getSourceInformation().publicationtitle)

    def test_source_getPrimaryPageImages(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(3,source.getPrimaryPageImages().count())
        first=source.getPrimaryPageImages()[0]
        self.assertEqual(u"p. 9 Music,  bs 156\u2013171",first.textlabel)


    def test_source_getPages(self):
        source=Source.objects.get(id=17890)
        self.assertEqual(9,source.getPages().count())
        first=source.getPages()[0]
        self.assertEqual("3",first.label)

    def test_source_getFirstBarRegion(self):
        source=Source.objects.get(id=17890)
        self.assertNotEqual(None,source.getFirstBarRegion())
        self.assertEqual(3079,source.getFirstBarRegion().x)


    def test_sourcecomponent_getPages(self):
        sc=SourceComponent.objects.get(id=36496)
        self.assertEqual(9, sc.getPages().count())
        last=sc.getPages().reverse()[0]
        self.assertEqual("11",last.label)


    def test_pageimage_getInstruments(self):
        pageimage=PageImage.objects.get(id=61539)
        self.assertEqual(1,pageimage.getInstruments().count())
        i=pageimage.getInstruments()[0]
        self.assertEqual("Piano",i.instrument)


    def test_page_getPrimaryPageImage(self):
        default_page=Page.objects.get(id=61539)
        self.assertEqual(u"p. 9 Music,  bs 156\u2013171",default_page.getPrimaryPageImage().textlabel)


    def test_page_getWorkComponent(self):
        default_page=Page.objects.get(id=61533)
        self.assertEqual(u"Music",default_page.getWorkComponent().label)
