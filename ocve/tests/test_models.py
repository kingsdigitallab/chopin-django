# -*- coding: utf-8 -*-
__author__ = 'Elliott Hall'

from django.test import TestCase

from ocve.uiviews import *


class TestModels(TestCase):
    fixtures = ['test_models_fixtures.json']

    def setUp(self):
        self.expected_work=Work.objects.get(id=6337)
        self.expected_sources=Source.objects.filter(id=17890)
        self.expected_highest_bar_number=186
        self.expected_lowest_bar_number=183
        self.expected_highest_bar=Bar.objects.get(barnumber=186)
        self.expected_opus=Opus.objects.get(id=6611)
        self.expected_accode="38–1-B&H"
        self.expected_accodeobject=AcCode.objects.get(id=2887)
        self.expected_sourcecomponents=SourceComponent.objects.all()
        self.expected_sourceinformation=SourceInformation.objects.get(id=17522)
        self.expected_primarypageimages=PageImage.objects.filter(versionnumber=1)
        self.expected_pages=Page.objects.filter(sourcecomponent__source=self.expected_sources[0])
        self.expected_firstbarregion=BarRegion.objects.get(id=183)
        self.default_sourcecomponent=SourceComponent.objects.get(id=36496)
        self.expected_sourcecomponent_pages=Page.objects.filter(sourcecomponent=self.default_sourcecomponent)
        i=Instrument(id=1,instrument="")
        i.save()
        SourceComponent_Instrument.create(instrument=i,sourcecomponent=self.default_sourcecomponent)
        self.expected_instruments=Instrument.objects.get(id=1)
        self.default_page=Page.objects.get(id=61533)
        self.expected_page_primarypageimage=PageImage.objects.filter(page=self.default_page)
        self.expected_workcomponent=WorkComponent.objects.get(id=9303)


    # Work
    def test_work_getSources(self):
        work=self.expected_work
        sources=work.getSources()
        self.assertEqual(sources, self.expected_sources)

    #BarRegion
    def test_barregion_getHighestBarNumber(self):
        barregion=BarRegion.objects.get(id=269389)
        self.assertEqual(barregion.getHighestBarNumber(),self.expected_highest_bar_number)

    def test_barregion_getLowestBarNumber(self):
        barregion=BarRegion.objects.get(id=269392)
        self.assertEqual(barregion.getLowestBarNumber(),self.expected_lowest_bar_number)

    def test_barregion_getHighestBar(self):
        barregion=BarRegion.objects.get(id=269389)
        self.assertEqual(barregion.getHighestBar(),self.expected_highest_bar)

    #Source

    def test_source_getWork(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getWork(),self.expected_work)


    #w.label+" "+self.label
    def test_source_getOpusLabel(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getOpusLabel(),"Ballade Op. 38 GFE: first impression (G)")

    def test_source_getAcCode(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getAcCode(),"38–1-B&H")


    def test_source_getAcCodeObject(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getAcCodeObject(),self.expected_accode)


    def test_source_getSourceComponents(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getSourceComponents(),self.expected_sourcecomponents)


    def test_source_getSourceInformation(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getSourceInformation,self.expected_sourceinformation)

    def test_source_getPrimaryPageImages(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getPrimaryPageImages(),self.expected_primarypageimages)

    def test_source_getPages(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getPages(),self.expected_pages)

    def test_source_getFirstBarRegion(self):
        source=self.expected_sources[0]
        self.assertEqual(source.getFirstBarRegion(),self.expected_firstbarregion)


    def test_sourcecomponent_getPages(self):
        sc=self.default_sourcecomponent
        self.assertEqual(sc.getPages(),self.expected_sourcecomponent_pages)


    def test_pageimage_getInstruments(self):
        self.assertEqual(self.default_page.pageimage.getInstruments(),self.expected_instruments)


    def test_page_getPrimaryPageImage(self):
        self.assertEqual(self.default_page.getPrimaryPageImage(),self.expected_page_primarypageimage)


    def test_page_getWorkComponent(self):
        self.assertEqual(self.default_page.getWork(),self.expected_work)
