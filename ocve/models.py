from django.db import models
from django.conf import settings
from models import *
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.db import models
from django.utils.encoding import force_unicode

import hashlib

# Create your models here.

def getUnicode(object):
    if (object == None):
        return u""
    else:
        return force_unicode(object)


#
class WorkComponent(models.Model):
    orderno = models.IntegerField(null=True, blank=True, )
    label = models.TextField(null=False, default="", blank=True, )
    music = models.IntegerField(null=True, blank=True, )
    work = models.ForeignKey('Work', blank=False, null=False, default=1, )
    keymode = models.ForeignKey('keyMode', blank=False, null=False, default=1, )
    keypitch = models.ForeignKey('keyPitch', blank=False, null=False, default=1, )
    opus = models.ForeignKey('Opus', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'WorkComponent'
        verbose_name_plural = 'WorkComponents'


    table_group = ''


#
class Work(models.Model):
    complete = models.BooleanField(default=False, null=False, blank=False, )
    label = models.TextField(null=False, default="", blank=True, )
    genre = models.ManyToManyField('Genre', blank=False, null=False, default=1, through='Genre_Work', )
    workinformation = models.ForeignKey('WorkInformation', blank=False, null=False, default=1, )
    workcollection = models.ForeignKey('WorkCollection', blank=False, null=False, default=2, )
    orderno = models.IntegerField(null=True, blank=True, )
    class Meta:
        verbose_name = 'Work'
        verbose_name_plural = 'Works'
        ordering=['orderno']


    table_group = ''
    def getSources(self):
        sources = Source.objects.filter(sourcecomponent__sourcecomponent_workcomponent__workcomponent__work=self).distinct()
        return sources

#
class Opus(models.Model):
    opusno = models.IntegerField(null=True, blank=True, )

    class Meta:
        verbose_name = 'Opus'
        verbose_name_plural = 'Opuses'

Opus._meta.ordering = ["opusno"]



#
class BarRegion(models.Model):
    x = models.IntegerField(null=True, blank=True, )
    y = models.IntegerField(null=True, blank=True, )
    width = models.IntegerField(null=True, blank=True, )
    height = models.IntegerField(null=True, blank=True, )
    anomaly = models.IntegerField(null=False, blank=True,default=0 )
    annotation = models.ManyToManyField('Annotation', blank=True, null=True, through='Annotation_BarRegion', )
    pageimage = models.ForeignKey('PageImage', blank=False, null=False, default=1, )
    page = models.ForeignKey('Page', blank=False, null=False, default=1, related_name='barRegions', )
    barid_old = models.IntegerField(null=True, blank=True, )
    bar = models.ManyToManyField('Bar', blank=True, null=True,
        through='Bar_BarRegion', )

    def getHighestBarNumber(self):
        num=0
        for b in self.bar.all():
            num=b.barnumber
        return num

    def getLowestBarNumber(self):
        bars=self.bar.all().order_by('barnumber')
        if bars.count() >0:
            return bars[0].barnumber
        return 0

    def getHighestBar(self):
        bar=None
        for b in self.bar.all():
            bar=b
        return bar

    class Meta:
        verbose_name = 'BarRegion'
        verbose_name_plural = 'BarRegions'


    table_group = ''

#Initial population with:  insert into ocve2real.ocve_bar_barregion (bar_id,barregion_id) SELECT bar_id,id FROM ocve2real.ocve_barregion o;
class Bar_BarRegion(models.Model):
    bar = models.ForeignKey('Bar', blank=False, null=False, default=1, )
    barregion = models.ForeignKey('BarRegion', blank=False, null=False, default=1, )


#
class Bar(models.Model):
    barnumber = models.IntegerField(null=True, blank=True, )
    barlabel = models.TextField(null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'Bar'
        verbose_name_plural = 'Bars'


    table_group = ''


#
class Source(models.Model):
    label = models.TextField(null=False, default="", blank=True, )
    cfeolabel = models.TextField(null=False, default="", blank=True, )
    sourcetype = models.ForeignKey('SourceType', blank=False, null=False, default=1, )
    ocve=models.BooleanField(default=False)
    cfeo=models.BooleanField(default=False)
    orderno=models.IntegerField(blank=False, null=False, default=999)

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        ordering = ["orderno"]

    def setWork(self):
        pass

    def getWork(self):
        works=Work.objects.filter(workcomponent__sourcecomponent_workcomponent__sourcecomponent__source=self).distinct()
        if works is not None and works.__len__()>0:
            return works[0]
        else:
            return None

    def getOpusLabel(self):
        w = self.getWork()
        if w is not None:
            return w.label+" "+self.label
        else:
            return self.label

    def getAcCode(self):
        try:
            si=SourceInformation.objects.get(source=self)
            return si.accode.accode
        except ObjectDoesNotExist:
            return ""
        except MultipleObjectsReturned:
            return ""

    def getAcCodeObject(self):
        try:
            si = SourceInformation.objects.get(source=self)
            return si.accode
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            return None

    def getSourceComponents(self):
        try:
            comps=SourceComponent.objects.filter(source=self)
            return comps
        except ObjectDoesNotExist:
            pass

    def getSourceInformation(self):
        si=SourceInformation.objects.filter(source=self)
        if si.count() >0:
            return si[0]
        else:
            return None

    #All instruments attached to a particular source
    def getInstruments(self):
        return Instrument.objects.filter(sourcecomponent_instrument__sourcecomponent__source=self).distinct()

    def getPrimaryPageImages(self):
        pi=PageImage.objects.filter(page__sourcecomponent__source=self,versionnumber=1).order_by("page")
        return pi

    def getPages(self):
        return Page.objects.filter(sourcecomponent__source=self)
    table_group = ''

    def getFirstBarRegion(self):
        try:
            return BarRegion.objects.filter(pageimage__page__sourcecomponent__source=self).order_by('pageimage__page','bar')[0]
        except ObjectDoesNotExist:
            return None
        except IndexError:
            return None


#
class Genre(models.Model):
    genre = models.CharField(max_length=255, null=False, default="", blank=True, )
    pluralname = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'


    table_group = ''


#
class keyPitch(models.Model):
    keypitch = models.CharField(max_length=255, null=False, default="", blank=True, )
    orderno = models.IntegerField(null=False, default=0, )
    class Meta:
        ordering=['orderno']
        verbose_name = 'keyPitch'
        verbose_name_plural = 'keyPitches'


    table_group = ''


#
class Instrument(models.Model):
    instrument = models.CharField(max_length=255, null=False, default="", blank=True, )
    instrumentabbrev = models.CharField(max_length=128, null=False, default="", blank=True, )
    sourcecomponent = models.ManyToManyField('SourceComponent', blank=True, null=True,
                                             through='SourceComponent_Instrument', )

    class Meta:
        verbose_name = 'Instrument'
        verbose_name_plural = 'Instruments'


    table_group = ''


#
class keyMode(models.Model):
    keymode = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'keyMode'
        verbose_name_plural = 'keyModes'


    table_group = ''


#
class SourceComponent(models.Model):
    orderno = models.IntegerField(null=True, blank=True, )
    label = models.TextField(null=False, default="", blank=True, )
    instrumentnumber = models.IntegerField(null=True, blank=True, )
    instrumentkey = models.CharField(max_length=128, null=False, default="", blank=True, )
    overridelabel = models.TextField(null=False, default="", blank=True, )
    sourcecomponenttitle = models.CharField(max_length=255, null=False, default="", blank=True,
                                            help_text=ur'''e.g song titles like "Wojack"''', )
    source = models.ForeignKey('Source', blank=False, null=False, default=1, )
    sourcecomponenttype = models.ForeignKey('SourceComponentType', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'SourceComponent'
        verbose_name_plural = 'SourceComponents'
        ordering = ["orderno"]


    table_group = ''

    def getPages(self):
        try:
            pages = Page.objects.filter(sourcecomponent=self)
            return pages
        except ObjectDoesNotExist:
            pass


#
class Publisher(models.Model):
    publisher = models.TextField(null=False, default="", blank=True, )
    notes = models.TextField(null=False, default="", blank=True, )
    publisherAbbrev = models.CharField(max_length=45, null=False, default="", blank=True)

class Meta:
    ordering = ['publisher']
    verbose_name = 'Publisher'
    verbose_name_plural = 'Publishers'

    def __unicode__(self):
        return u'%s' % (self.publisher)


table_group = ''


#
class WorkComponentType(models.Model):
    type = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'WorkComponentType'
        verbose_name_plural = 'WorkComponentTypes'


    table_group = ''


#
class instrumentComponent(models.Model):
    instrument = models.ForeignKey('Instrument', blank=False, null=False, default=1, )
    sourcecomponent = models.ForeignKey('SourceComponent', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'instrumentComponent'
        verbose_name_plural = 'instrumentComponents'


    table_group = ''


#
class WorkCollection(models.Model):
    label = models.TextField(null=False, default="", blank=True, )
    overridelabel = models.TextField(null=False, default="", blank=True, )
    collectiontype = models.ForeignKey('CollectionType', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'WorkCollection'
        verbose_name_plural = 'WorkCollections'


    table_group = ''


#
class SourceInformation(models.Model):
    platenumber = models.CharField(max_length=255, null=False, default="", blank=True, )
    locationsimilarcopies = models.TextField(null=False, default="", blank=True, )
    reprints = models.TextField(null=False, default="", blank=True, )
    seriestitle = models.CharField(max_length=255, null=False, default="", blank=True, )
    copyright = models.CharField(max_length=255, null=False, default="", blank=True, )
    contentssummary = models.CharField(max_length=255, null=False, default="", blank=True, )
    contents = models.TextField(null=False, default="", blank=True,)# help_text=ur'''Edition text''', )
    shelfmark = models.CharField(max_length=255, null=False, default="", blank=True, )
    notes = models.TextField(null=False, default="", blank=True, )
    datepublication = models.CharField(max_length=255, null=False, default="", blank=True, )
    placepublication = models.ForeignKey('City', null=True, blank=True, )
    leaves = models.CharField(max_length=255, null=False, default="", blank=True, )
    sourcecode = models.CharField(max_length=255, null=False, default="", blank=True, )
    title = models.TextField(null=False, default="", blank=True, )
    publicationtitle = models.TextField(null=False, default="", blank=True, )
    imagesource = models.CharField(max_length=255, null=False, default="", blank=True, )
    additionalInformation=models.TextField(null=False, default="", blank=True, )
    keyFeatures=models.TextField(null=False, default="", blank=True, )
    volume = models.CharField(max_length=255, null=False, default="", blank=True, )
    source = models.ForeignKey('Source', blank=False, null=False, default=1, )
    publisher = models.ForeignKey('Publisher', blank=False, null=False, default=1, )
    archive = models.ForeignKey('Archive', blank=False, null=False, default=1, )
    dedicatee = models.ForeignKey('Dedicatee', blank=False, null=False, default=1, )
    accode = models.ForeignKey('AcCode', blank=False, null=False, default=1, )
    displayedcopy = models.CharField(max_length=255, null=False, default="", blank=True, )
    printingmethod = models.ManyToManyField('PrintingMethod',through='SourceInformation_PrintingMethod',default=1)


    class Meta:
        verbose_name = 'SourceInformation'
        verbose_name_plural = 'SourceInformations'


    table_group = ''

#
class BarSequence(models.Model):
    #pageimage = models.ForeignKey('PageImage', blank=False, null=False,)
    startbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    endbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

#
class PageImage(models.Model):
    surrogate = models.IntegerField(null=True, blank=True, )
    textlabel = models.TextField(null=False, default="", blank=True, )
    versionnumber = models.IntegerField(null=True, blank=True, )
    permission = models.BooleanField(default=False, null=False, blank=False, )
    permissionnote = models.CharField(max_length=255, null=False, default="", blank=True, )
    height = models.IntegerField(null=True, blank=True, )
    width = models.IntegerField(null=True, blank=True, )
    startbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    endbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    corrected = models.IntegerField(null=True, blank=True, )
    page = models.ForeignKey('Page', blank=False, null=False, default=1, )
    barsequences = generic.GenericRelation(BarSequence, null=True, blank=True)

    def getInstruments(self):
        return Instrument.objects.filter(sourcecomponent_instrument__sourcecomponent__page__pageimage=self).distinct()

    class Meta:
        verbose_name = 'PageImage'
        verbose_name_plural = 'PageImages'

    table_group = ''

#
class PageType(models.Model):
    type = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'PageType'
        verbose_name_plural = 'PageTypes'

    table_group = ''

#
class CollectionType(models.Model):
    type = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'CollectionType'
        verbose_name_plural = 'CollectionTypes'


    table_group = ''


#
class SourceComponentType(models.Model):
    type = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'SourceComponentType'
        verbose_name_plural = 'SourceComponentTypes'


    table_group = ''


#
class Page(models.Model):
    label = models.TextField(null=False, default="", blank=True, )
    orderno = models.IntegerField(null=True, blank=True, )
    preferredversion = models.IntegerField(null=True, blank=True, default=1 )
    sourcecomponent = models.ForeignKey('SourceComponent', blank=False, null=False, default=1, )
    pagetype = models.ForeignKey('PageType', blank=False, null=False, default=1, )

    def getWorkComponent(self):
        wc=WorkComponent.objects.filter(sourcecomponent_workcomponent__sourcecomponent__page=self)
        if wc.count() > 0:
            return wc[0]
        return None

    def getPrimaryPageImage(self):
        pi=PageImage.objects.filter(page=self,versionnumber=1)
        if pi.count() > 0:
            return pi[0]
        return None

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'


    table_group = ''


#
class Archive(models.Model):
    name = models.TextField(null=False, default="", blank=True, )
    siglum = models.CharField(max_length=255, null=False, default="", blank=True, )
    notes = models.TextField(null=False, default="", blank=True, )
    city = models.ForeignKey('City', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'Archive'
        verbose_name_plural = 'Archives'


    table_group = ''


#
class City(models.Model):
    city = models.CharField(max_length=255, null=False, default="", blank=True, )
    country = models.ForeignKey('Country', blank=False, null=False, default=1, related_name='1', )

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return u'%s' % (self.city)


    table_group = ''


#
class Country(models.Model):
    country = models.CharField(max_length=255, null=False, default="", blank=True, )
    countryabbrev = models.CharField(max_length=128, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


    table_group = ''


#
class SourceType(models.Model):
    type = models.CharField(max_length=255, null=False, default="", blank=True, )

    class Meta:
        verbose_name = 'SourceType'
        verbose_name_plural = 'SourceTypes'


    table_group = ''


#
class Year(models.Model):
    year = models.IntegerField(null=True, blank=True, )
    sourceinformation = models.ManyToManyField('SourceInformation', blank=False, null=False, default=1,
                                               through='SourceInformation_Year', )

    class Meta:
        ordering = ['year']
        verbose_name = 'Year'
        verbose_name_plural = 'Years'


    table_group = ''


#
class Dedicatee(models.Model):
    dedicatee = models.TextField(null=False, default="", blank=True, )
    alternateOf = models.ForeignKey('Dedicatee', blank=False, null=False, default=1,related_name="alternate" )

    class Meta:
        ordering = ['dedicatee']
        verbose_name = 'Dedicatee'
        verbose_name_plural = 'Dedicatees'



    table_group = ''


#
class PrintingMethod(models.Model):
    method = models.CharField(max_length=255, null=False, default="", blank=True, )


    class Meta:
        verbose_name = 'PrintingMethod'
        verbose_name_plural = 'PrintingMethods'


    table_group = ''


#
class WorkInformation(models.Model):
    generalinfo = models.TextField(null=False, default="", blank=True,
                                   help_text=ur'''Publication History for this work''', )
    relevantmanuscripts = models.TextField(null=False, default="", blank=True, )
    analysis = models.TextField(null=False, default="", blank=True, )
    OCVE= models.TextField(null=False, default="", blank=True,help_text=ur'Only field displayed in OCVE work summary' )
    class Meta:
        verbose_name = 'WorkInformation'
        verbose_name_plural = 'WorkInformations'


    table_group = ''


class AnnotationType(models.Model):
    annotationType = models.CharField(max_length=255, null=False, default="", blank=True, )



class Annotation(models.Model):
    user = models.ForeignKey(User,default=11)
    notetext = models.TextField(null=False, default="", blank=True, )
    noteregions = models.TextField(null=False, default="", blank=True, )
    pageimage = models.ForeignKey('PageImage', blank=False, null=False, default=1 )
    type = models.ForeignKey('AnnotationType', blank=False, null=False, default=1)
    timestamp=models.DateTimeField(auto_now=True)

    def getBarRegions(self):
        return BarRegion.objects.filter(annotation_barregion__annotation=self)


    class Meta:
        verbose_name = 'Annotation'
        verbose_name_plural = 'Annotations'


    table_group = ''

class BarCollection(models.Model):
    user = models.ForeignKey(User,default=11)
    name = models.TextField(null=False, default="", blank=True, )
    xystring = models.TextField(null=False, default="", blank=True, )
    regions = models.ManyToManyField(BarRegion)


#
class AcCode(models.Model):
    accode = models.CharField(max_length=255, null=False, default='',
                              blank=True, unique=True)
    accode_hash = models.CharField(max_length=256, editable=False)
    #sourceinformation = models.ForeignKey('SourceInformation', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'AcCode'
        verbose_name_plural = 'AcCodes'
        ordering = ["accode"]

    table_group = ''


# Many To Many Tables

#
class SourceInformation_Year(models.Model):
    sourceinformation = models.ForeignKey('SourceInformation')
    year = models.ForeignKey('Year')

#
class SourceComponent_Instrument(models.Model):
    sourcecomponent = models.ForeignKey('SourceComponent')
    instrument = models.ForeignKey('Instrument')

class SourceComponent_WorkComponent(models.Model):
    sourcecomponent = models.ForeignKey('SourceComponent')
    workcomponent = models.ForeignKey('WorkComponent')
#
class SourceInformation_PrintingMethod(models.Model):
    sourceinformation = models.ForeignKey('SourceInformation')
    printingmethod = models.ForeignKey('PrintingMethod')

#
class Genre_Work(models.Model):
    genre = models.ForeignKey('Genre')
    work = models.ForeignKey('Work')

    class Meta:
        ordering = ['work']

#
class Annotation_BarRegion(models.Model):
    annotation = models.ForeignKey('Annotation')
    barregion = models.ForeignKey('BarRegion')



class BarSpine(models.Model):
    label = models.TextField(null=False, default="", blank=True, )
    bar = models.ForeignKey('Bar', blank=False, null=False, default=1 )
    #page = models.ForeignKey('Page', blank=False, null=False, default=1 )
    sourcecomponent = models.ForeignKey('SourceComponent', blank=False, null=False, default=1 )
    orderNo = models.IntegerField(null=True, blank=True,default=0 )
    source = models.ForeignKey('Source', blank=False, null=False, default=1 )
    implied=models.IntegerField(null=True, blank=True,default=0 )


def country_unicode(self):
    return self.country

Country.__unicode__=country_unicode
Country._meta.ordering = ["country"]


def archive_unicode(self):
    return self.name

Archive.__unicode__=archive_unicode
Archive._meta.ordering = ["name"]

def work_unicode(self):
    return self.label

Work.__unicode__=work_unicode
Work._meta.ordering = ["orderno"]

def workComponent_unicode(self):
    return self.label

WorkComponent.__unicode__=workComponent_unicode
WorkComponent._meta.ordering = ["orderno"]

def source_unicode(self):
    return self.label
Source._meta.ordering = ["label"]

Source.__unicode__=source_unicode

def sourcet_unicode(self):
    return self.type

SourceType.__unicode__=sourcet_unicode

def sourcect_unicode(self):
    return self.type

SourceComponentType.__unicode__=sourcect_unicode

def WorkInformation_unicode(self):
    return str(self.id)

WorkInformation.__unicode__=WorkInformation_unicode

def PrintingMethod_unicode(self):
    return self.method

PrintingMethod.__unicode__=PrintingMethod_unicode

def SourceComponent_unicode(self):
    out=''
#    works=Work.objects.filter(workcomponent__sourcecomponent_workcomponent__sourcecomponent=self)
#    for w in works:
#        out+=w.label+" "
    out +=self.label
    return out

def getWorkComponentLabel(self):
    label=''
    try:
        wc=WorkComponent.objects.get(sourcecomponent_workcomponent__sourcecomponent=self)
        label=wc.label
    except ObjectDoesNotExist:
        pass
    except MultipleObjectsReturned:
        pass
    return label

SourceComponent.getWorkComponentLabel=getWorkComponentLabel
SourceComponent.__unicode__=SourceComponent_unicode


def page_unicode(self):
    return self.label

#class Page(Page):
 #     class Meta:
  #      ordering = ["orderno"]

Page.__unicode__=page_unicode
Page._meta.ordering = ["orderno"]






#PageImage._meta.order_with_respect_to='page'

def barregion_unicode(self):
    label=''
    for b in self.bar.all():
        label+=b.barlabel
    return label

#class BarRegion(BarRegion):
 #     class Meta:
  #      ordering = ["bar.barnumber"]

BarRegion.__unicode__=barregion_unicode
#BarRegion._meta.ordering = ["bar.barnumber"]

def opus_unicode(self):
    return str(self.opusno)

Opus.__unicode__=opus_unicode
Opus._meta.ordering = ["opusno"]

def keyPitch_unicode(self):
    return self.keypitch

keyPitch.__unicode__=keyPitch_unicode
keyPitch._meta.ordering = ["orderno"]

#class toneNote(toneNote):

def keyMode_unicode(self):
    return self.keymode

keyMode.__unicode__=keyMode_unicode
keyMode._meta.ordering = ["keymode"]

def bar_unicode(self):
    return self.barlabel

#class Bar(Bar):

Bar.__unicode__=bar_unicode
Bar._meta.ordering = ["barnumber","barlabel"]

def pub_unicode(self):
    return self.publisher
Publisher.__unicode__=pub_unicode
Publisher._meta.ordering=["publisher"]

def ins_unicode(self):
    return self.instrument

Instrument.__unicode__=ins_unicode
Instrument._meta.ordering=["instrument"]

def genre_unicode(self):
    return self.genre
Genre.__unicode__=genre_unicode
Genre._meta.ordering = ["genre"]

def workc_unicode(self):
    return self.label
WorkCollection.__unicode__=workc_unicode


def ac_unicode(self):
    return self.accode

AcCode.__unicode__=ac_unicode

def save(self, *args, **kwargs):
    self.accode_hash = hashlib.md5(self.accode.encode('UTF-8')).hexdigest()
    super(AcCode, self).save(*args, **kwargs)

AcCode.save = save


def dedicatee_unicode(self):
    return self.dedicatee

Dedicatee.__unicode__=dedicatee_unicode

class EditStatus(models.Model):
    status = models.CharField(max_length=255, null=False, default="NONE", blank=True, )

def sourcestatus_unicode(self):
    return self.status

EditStatus.__unicode__=sourcestatus_unicode
EditStatus._meta.ordering = ["id"]

class SourceLegacy(models.Model):
     cfeoKey = models.IntegerField(null=True, blank=True,default=0 )
     witnessKey = models.IntegerField(null=True, blank=True,default=0 )
     source = models.ForeignKey('Source', blank=False, null=False, default=1 )
     sourceDesc = models.TextField(null=False, default="", blank=True, )
     editstatus =  models.ForeignKey('EditStatus', blank=False, null=False, default=1, )
     mellon = models.BooleanField(default=False, null=False, blank=False)
     needsBarLines = models.BooleanField(default=False, null=False, blank=False)

class PageLegacy(models.Model):
    ocveKey = models.IntegerField(null=True, blank=True, )
    cfeoKey = models.IntegerField(null=True, blank=True, )
    filename = models.TextField(null=False, default="", blank=True, )
    storageStructure = models.TextField(null=False, default="", blank=True, )
    pageimage = models.ForeignKey('PageImage', blank=False, null=False, default=1, )
    cropCorrected = models.IntegerField(null=True, blank=True, default=0)
    editstatus =  models.ForeignKey('EditStatus', blank=False, null=False, default=1, )
    jp2=models.CharField(max_length=255, null=False, default="UNVERIFIED", blank=True, )

    class Meta:
        verbose_name = 'Page Legacy'
        verbose_name_plural = 'Page Legacy'

#For brand new images for brand new sources
#Moved to normal structure after audit

class NewPageImage(models.Model):
    surrogate = models.IntegerField(null=True, blank=True, )
    versionnumber = models.IntegerField(null=True, blank=True, )
    permission = models.BooleanField(default=False, null=False, blank=False, )
    permissionnote = models.CharField(max_length=255, null=False, default="", blank=True, )
    height = models.IntegerField(null=True, blank=True, )
    width = models.IntegerField(null=True, blank=True, )
    filename = models.CharField(max_length=255, null=False, default="", blank=True, )
    startbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    endbar = models.CharField(max_length=255, null=False, default="", blank=True, )
    corrected = models.IntegerField(null=True, blank=True, default=0)
    linked = models.IntegerField(null=True, blank=True, default=0) #>0 if it is saved in pages/page images
    source = models.ForeignKey('NewSource', blank=False, null=False, default=1, )
    barsequences = generic.GenericRelation(BarSequence, null=True, blank=True)

    class Meta:
        verbose_name = 'NewPageImage'
        verbose_name_plural = 'NewPageImages'

class NewSource(models.Model):
    label = models.TextField(null=False, default="", blank=True, )
    library = models.TextField(null=False, default="", blank=True, )
    copyright = models.TextField(null=False, default="", blank=True, )
    sourcecode=models.CharField(max_length=255, null=False, default="", blank=True, )
    sourcecreated = models.IntegerField(null=False, blank=False,default=0 )

def newSource_unicode(self):
    label="no library given"
    if self.library is not None:
        label=self.library
    if self.sourcecode is not None:
        label=label+" - "+self.sourcecode
    return label

NewSource.__unicode__= newSource_unicode


class NewSourceInformation(models.Model):
    platenumber = models.CharField(max_length=255, null=False, default="", blank=True, )
    locationsimilarcopies = models.TextField(null=False, default="", blank=True, )
    reprints = models.TextField(null=False, default="", blank=True, )
    seriestitle = models.CharField(max_length=255, null=False, default="", blank=True, )
    copyright = models.CharField(max_length=255, null=False, default="", blank=True, )
    contentssummary = models.CharField(max_length=255, null=False, default="", blank=True, )
    contents = models.TextField(null=False, default="", blank=True, help_text=ur'''Edition text''', )
    shelfmark = models.CharField(max_length=255, null=False, default="", blank=True, )
    notes = models.TextField(null=False, default="", blank=True, )
    datepublication = models.CharField(max_length=255, null=False, default="", blank=True, )
    leaves = models.IntegerField(null=True, blank=True, )
    sourcecode = models.CharField(max_length=255, null=False, default="", blank=True, )
    title = models.TextField(null=False, default="", blank=True, )
    publicationtitle = models.TextField(null=False, default="", blank=True, )
    imagesource = models.CharField(max_length=255, null=False, default="", blank=True, )
    platenumber = models.CharField(max_length=255, null=False, default="", blank=True, )
    additionalInformation=models.TextField(null=False, default="", blank=True, )
    keyFeatures=models.TextField(null=False, default="", blank=True, )
    volume = models.CharField(max_length=255, null=False, default="", blank=True, )
    source = models.ForeignKey('NewSource', blank=False, null=False, default=1, )
    publisher = models.ForeignKey('Publisher', blank=False, null=False, default=1, )
    archive = models.ForeignKey('Archive', blank=False, null=False, default=1, )
    dedicatee = models.ForeignKey('Dedicatee', blank=False, null=False, default=1, )
    accode = models.ForeignKey('AcCode', blank=False, null=False, default=1, )

    class Meta:
        verbose_name = 'SourceInformation'
        verbose_name_plural = 'SourceInformations'



def getEditStatus(self):
    try:
        sl=SourceLegacy.objects.get(source=self)
        return sl.editstatus
    except ObjectDoesNotExist:
        return ""

def getLegacy(self):
    try:
        sl=SourceLegacy.objects.get(source=self)
        return sl
    except ObjectDoesNotExist:
        return ""

Source.getEditStatus=getEditStatus
Source.getLegacy=getLegacy

def getYears(self):
    return Year.objects.filter(sourceinformation_year__sourceinformation=self)

SourceInformation.getYears=getYears

def getJP2Path(self):
    pl = PageLegacy.objects.get(pageimage=self)
    jp2 = pl.jp2
    if str(jp2).startswith('jp2/') is False:
        jp2='jp2/'+jp2
    return jp2


    #TODO: Simplify this once image name rationalisation complete
def getZoomifyPath(self):
    fullurl = settings.IIP_URL+'?zoomify='
    #pl = PageLegacy.objects.get(pageimage=self)
    jp2=self.getJP2Path()
    fullurl = fullurl + jp2 +'/'
    return fullurl

PageImage.getJP2Path=getJP2Path
PageImage.getZoomifyPath=getZoomifyPath

def annotationType_unicode(self):
    return self.annotationType
AnnotationType.__unicode__=annotationType_unicode

def year_unicode(self):
    return str(self.year)
Year.__unicode__=year_unicode


