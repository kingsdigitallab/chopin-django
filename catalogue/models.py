import hashlib
import logging
from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.utils.text import slugify
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel,
                                         PageChooserPanel)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.core.templatetags.wagtailcore_tags import pageurl
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents.models import Document
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.formats import Format, register_image_format
from wagtail.images.models import Image
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from .behaviours import Introducable

logger = logging.getLogger(__name__)

register_image_format(Format('left-100', 'Left-aligned 100px',
                             'richtext-image left', 'width-100'))
register_image_format(Format('left-200', 'Left-aligned 200px',
                             'richtext-image left', 'width-200'))
register_image_format(Format('left-300', 'Left-aligned 300px',
                             'richtext-image left', 'width-300'))
register_image_format(Format('left-400', 'Left-aligned 400px',
                             'richtext-image left', 'width-400'))


def _d(str):
    return str.decode(settings.AC_ENCODING)


def _e(str):
    return str.encode(settings.AC_ENCODING)


def safe_slugify(text, model):
    """Return a slugified version of `text` that copes with the brain dead
    nature of Wagtail, which uses slugs as lookup keys and has a 50
    character limit on them."""
    slug = slugify(text)[:48]
    num = 1
    while True:
        try:
            model.objects.get(slug=slug)
            slug += '-{}'.format(num)
            num += 1
        except model.DoesNotExist:
            break
    return slug


class HomePage(Page):
    content = RichTextField()
    search_fields = Page.search_fields + [index.SearchField('content'),]
    search_name = 'Home Page'
    subpage_types = ['IndexPage', 'RichTextPage']

    class Meta:
        verbose_name = 'homepage'


HomePage.content_panels = [
    FieldPanel('title', classname='full title'),
    # FieldPanel('content', classname='full'),
]



class IndexPage(Page, Introducable):
    search_name = 'Index Page'
    search_fields = Page.search_fields + [index.SearchField('introduction'),]
    subpage_types = ['IndexPage', 'RichTextPage', 'LibraryIndexPage',
                     'PublisherIndexPage', 'AbbreviationIndexPage']


IndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]



class LandingPageSection(Orderable):
    landing_page = ParentalKey('LandingPage', related_name='sections')
    title = models.CharField(max_length=256)
    abbreviation = models.CharField(max_length=32)
    css_class = models.CharField(max_length=64)
    introduction = RichTextField()
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('abbreviation', classname='full'),
        FieldPanel('css_class', classname='full'),
        FieldPanel('introduction', classname='full'),
        ImageChooserPanel('image'),
        PageChooserPanel('page', 'catalogue.HomePage')
    ]


class LandingPage(Page, Introducable):
    search_fields = Page.search_fields + [index.SearchField('introduction'),]
    search_name = 'Landing Page'
    subpage_types = ['HomePage']


LandingPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
    InlinePanel('sections', label='Sections'),
]





class RichTextPage(Page):
    content = RichTextField()

    search_fields = Page.search_fields + [index.SearchField('content'),]
    search_name = 'Rich Text Page'
    subpage_types = []



# RichTextPage.content_panels += [FieldPanel('content', classname='full')]


class Country(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)

    panels = [
        FieldPanel('name', classname='full title'),
    ]

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    @property
    def libraries(self):
        return Library.objects.filter(city__country=self)

    @property
    def publishers(self):
        return Publisher.objects.filter(city__country=self)


register_snippet(Country)


class City(TimeStampedModel):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(
        Country, related_name='cities', on_delete=models.CASCADE
    )

    panels = [
        FieldPanel('name', classname='full title'),
        SnippetChooserPanel('country', Country)
    ]

    class Meta:
        ordering = ['name']
        unique_together = ['country', 'name']
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return '{0}'.format(self.name)

    def __str__(self):
        return self.__unicode__()


register_snippet(City)


class Library(Page):
    name = models.CharField(max_length=256)
    city = models.ForeignKey(
        City, blank=True, null=True, on_delete=models.PROTECT,
        related_name='libraries')
    library_url = models.URLField(blank=True, null=True)
    pdf = models.ForeignKey(Document, null=True, blank=True,
                            on_delete=models.PROTECT, related_name='+')

    class Meta:
        ordering = ['title', 'city', 'name']
        verbose_name_plural = 'Libraries'

    def __unicode__(self):
        return '{0}: {1}'.format(self.title, self.name)

    def __str__(self):
        return self.__unicode__()

    @property
    def impressions(self):
        impressions = sorted(Impression.objects.filter(
            copies__copy__library=self),
            key=lambda x: x.impression.work.work.sort_order +
                          float(x.impression.sort_order) / 1000)

        works = OrderedDict()

        for impression in impressions:
            work = impression.work.work

            if not work in works:
                works[work] = []

            works[work].append(impression)

        return works


Library.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('name', classname='full title'),
    SnippetChooserPanel('city', City),
    FieldPanel('library_url', classname='full'),
    DocumentChooserPanel('pdf')
]


class LibraryIndexPage(RoutablePageMixin, Page, Introducable):
    search_name = 'Library Index Page'

    class Meta:
        verbose_name = 'Library Index Page'

    @property
    def libraries(self):
        return Library.objects.all()

    @route(r'^$', name='all_libraries')
    def serve_all_libraries(self, request):
        """Renders all the libraries."""
        return render(request, self.get_template(request),
                      {'self': self, 'libraries': self.libraries})

    @route(r'^libraries-by-city/$', name='libraries_by_city')
    def serve_libraries_by_city(self, request):
        """Renders libraries, grouped by city."""
        return render(request, self.get_template(request),
                      {'self': self, 'cities': City.objects.all()})

    @route(r'^libraries-by-country/$', name='libraries_by_country')
    def serve_libraries_by_country(self, request):
        """Renders libraries, grouped by country."""
        return render(request, self.get_template(request),
                      {'self': self, 'countries': Country.objects.all()})


LibraryIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]




class Publisher(Page):
    name = RichTextField(null=True, blank=True)
    abbreviation = models.CharField(max_length=256, null=True, blank=True)
    city = models.ForeignKey(
        City, blank=True, null=True, on_delete=models.PROTECT,
        related_name='publishers')

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        if self.name:
            return '{0}: {1}'.format(self.title, self.name)
        else:
            return self.title

    def __str__(self):
        return self.__unicode__()

    @property
    def sorted_impressions(self):
        return sorted(self.impressions.all(),
                      key=lambda x: x.impression.work.work.sort_order +
                                    float(x.impression.sort_order) / 1000)

    @property
    def works(self):
        works = []

        for impression in self.impressions.all():
            if impression.work not in works:
                works.append(impression.work)

        works = sorted(works, key=lambda x: x.work.sort_order)

        return works


Publisher.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('name', classname='full title'),
    FieldPanel('abbreviation', classname='full'),
    SnippetChooserPanel('city', City)
]

register_snippet(Publisher)


class PublisherIndexPage(RoutablePageMixin, Page, Introducable):

    @route(r'^$', name='all_publishers')
    def serve_all_publishers(self, request):
        """Renders all the publishers."""
        publishers = Publisher.objects.all()

        return render(request, self.get_template(request),
                      {'self': self, 'publishers': publishers})

    @route(r'^publishers-by-city/$', name='publishers_by_city')
    def serve_publishers_by_city(self, request):
        """Renders publishers, grouped by city."""
        return render(request, self.get_template(request),
                      {'self': self, 'cities': City.objects.all(),
                       'suburl': 'publishers-by-city'})

    @route(r'^publishers-by-country/$', name='publishers_by_country')
    def serve_publishers_by_country(self, request):
        """Renders publishers, grouped by country."""
        return render(request, self.get_template(request),
                      {'self': self, 'countries': Country.objects.all()})

    @route(r'^(?P<p_slug>.*?)/(?P<w_slug>.*?)/$', name='impressions')
    def serve_impressions(self, request, p_slug, w_slug):
        """Renders impressions for the given publisher and work."""
        publisher = Publisher.objects.filter(slug=p_slug).first()
        work = Work.objects.filter(slug=w_slug).first()

        impressions = []

        for impression in publisher.sorted_impressions:
            if impression.work.work == work:
                impressions.append(impression)

        return render(request, 'catalogue/publisher.html',
                      {'self': publisher, 'publisher': publisher, 'work': work,
                       'impressions': impressions})


PublisherIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]


class Copy(TimeStampedModel):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    description = models.TextField()

    panels = [
        PageChooserPanel('library', Library),
        FieldPanel('description', classname='full'),
    ]

    class Meta:
        verbose_name_plural = 'Copies'
        ordering = ['-created']

    def __unicode__(self):
        return str(self.library)

    def __str__(self):
        return self.__unicode__()


register_snippet(Copy)


class ImpressionCopy(Orderable, TimeStampedModel):
    impression = ParentalKey('Impression', related_name='copies')
    copy = models.ForeignKey(Copy, on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('copy', Copy)
    ]

    class Meta:
        ordering = ['sort_order']
        unique_together = ('impression', 'copy')

    def __unicode__(self):
        return '{0}: {1}'.format(self.impression, self.copy)

    def __str__(self):
        return self.__unicode__()


class Impression(Page):
    content = RichTextField()
    code_hash = models.CharField(max_length=32, editable=False)
    impression_title = models.TextField()
    ocve_ac_code = models.CharField(max_length=128, blank=True, null=True,
                                    verbose_name='AC Code in CFEO/OCVE')
    impression_publisher = models.ForeignKey(Publisher, blank=True, null=True,
                                  on_delete=models.PROTECT,
                                  related_name='impressions')
    comments = models.TextField()
    sort_order = models.PositiveIntegerField()
    pdf = models.ForeignKey(Document, null=True, blank=True,
                            on_delete=models.PROTECT, related_name='+')

    search_fields = (
        # index.SearchField('title', boost=10),
        index.SearchField('impression_title', partial_match=True, boost=10),
        #index.SearchField('content', partial_match=True)
    )
    search_name = 'Impression'

    class Meta:
        verbose_name = 'Impression'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        ac_code = self.title

        if self.ocve_ac_code:
            ac_code = self.ocve_ac_code

        self.code_hash = hashlib.md5(_e(ac_code)).hexdigest()
        super(Impression, self).save(*args, **kwargs)

    @property
    def work(self):
        return self.get_parent()


Impression.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('impression_title', classname='full title'),
    FieldPanel('ocve_ac_code', classname='full title'),
    PageChooserPanel('impression_publisher', Publisher),
    # FieldPanel('content', classname='full'),
    FieldPanel('comments', classname='full'),
    FieldPanel('sort_order'),
    DocumentChooserPanel('pdf'),
    InlinePanel('copies', label='Copies'),
]


class Work(Page):
    code = models.CharField(max_length=32)
    heading = models.TextField()
    has_opus = models.BooleanField(default=False)
    is_posthumous = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField()
    pdf = models.ForeignKey(Document, null=True, blank=True,
                            on_delete=models.PROTECT, related_name='+')

    search_fields = Page.search_fields + [
        index.SearchField('heading', partial_match=True),
    ]
    search_name = 'Work'
    subpage_types = ['Impression']

    class Meta:
        ordering = ['sort_order']
        verbose_name = 'Work'

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.__unicode__()

    @property
    def impressions(self):
        return self.get_children()


Work.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('code', classname='full'),
    FieldPanel('has_opus'),
    FieldPanel('is_posthumous'),
    FieldPanel('sort_order'),
    FieldPanel('heading', classname='full'),
    DocumentChooserPanel('pdf')
]


class Catalogue(RoutablePageMixin, Page, Introducable):
    search_name = 'Catalogue'
    subpage_types = ['Work']

    class Meta:
        verbose_name = 'Catalogue'

    @property
    def works(self):
        return self.get_children()

    @route(r'^$', name='all_works')
    def serve_all_works(self, request):
        """Renders all the works."""
        works = self.works

        return render(request, self.get_template(request),
                      {'self': self, 'works': works})

    @route(r'^works-with-opus/$', name='works_with_opus')
    def serve_works_with_opus(self, request):
        """Renders all the works that have opus number."""
        works = self.works.filter(work__has_opus=True,
                                  work__is_posthumous=False)

        return render(request, self.get_template(request),
                      {'self': self, 'works': works,
                       'subtitle': 'Works with opus numbers',
                       'suburl': 'works-with-opus'})

    @route(r'^posthumous-works-with-opus/$',
           name='posthumous_works_with_opus')
    def serve_posthumous_works_with_opus(self, request):
        """Renders all the posthumous works with opus number."""
        works = self.works.filter(work__has_opus=True,
                                  work__is_posthumous=True)

        return render(request, self.get_template(request),
                      {'self': self, 'works': works,
                       'subtitle': 'Posthumous works with opus numbers',
                       'suburl': 'posthumous-works-with-opus'})

    @route(r'^works-without-opus-numbers/$', name='works_without_opus')
    def serve_works_without_opus(self, request):
        """Renders all the works that don't have opus number."""
        works = self.works.filter(work__has_opus=False,
                                  work__is_posthumous=False)

        return render(request, self.get_template(request),
                      {'self': self, 'works': works,
                       'subtitle': 'Works without opus numbers',
                       'suburl': 'works-without-opus'})

    @route(r'^posthumous-works-without-opus/$',
           name='posthumous_works_without_opus')
    def serve_posthumous_works_without_opus(self, request):
        """Renders all the posthumous works without opus number."""
        works = self.works.filter(work__has_opus=False,
                                  work__is_posthumous=True)

        return render(request, self.get_template(request),
                      {'self': self, 'works': works,
                       'subtitle': 'Posthumous works without opus numbers',
                       'suburl': 'posthumous-works-without-opus'})

    @route(r'^impression/(?P<code_hash>.*?)/$',
           name='serve_impression_from_code_hash')
    def serve_impression_from_code_hash(self, request, code_hash):
        """Displays an impression from the hash of an ac code. This is used to
        connect from CFEO/OCVE."""
        impression = get_object_or_404(Impression, code_hash=code_hash)

        return redirect(pageurl(RequestContext(request), impression))


Catalogue.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]


class STP(TimeStampedModel):
    publisher = models.ForeignKey(Publisher, blank=True, null=True,
                                  on_delete = models.CASCADE,
                                  related_name='stps')
    publisher_name = models.CharField(max_length=256)
    publisher_name_slug = models.CharField(max_length=256, editable=False)
    rubric = RichTextField()
    rubric_slug = models.CharField(max_length=256, editable=False)
    pdf = models.ForeignKey(Document, blank=True, null=True,
                            on_delete=models.CASCADE, related_name='+')

    class Meta:
        ordering = ['publisher_name', 'rubric']
        verbose_name = 'Series Title Page'

    def __unicode__(self):
        return '{0}: {1}'.format(self.publisher_name, self.rubric)

    def __str__(self):
        return self.__unicode__()

    @property
    def url(self):
        index_page = Page.objects.filter(slug='i').first()
        stp_index_page = index_page.get_children().filter(
            slug='publishers').first()

        return '{0}{1}/{2}/'.format(stp_index_page.url,
                                    self.publisher_name_slug, self.rubric_slug)

    def save(self, *args, **kwargs):
        self.publisher_name_slug = slugify(self.publisher_name)
        self.rubric_slug = slugify(self.rubric)
        super(STP, self).save(*args, **kwargs)


STP.panels = [
    FieldPanel('rubric', classname='full title'),
    FieldPanel('publisher_name', classname='full'),
    SnippetChooserPanel('publisher', Publisher),
    DocumentChooserPanel('pdf')
]

register_snippet(STP)


class STPIndexPage(RoutablePageMixin, Page):
    introduction = RichTextField(blank=True)

    search_name = 'STP Index Page'

    class Meta:
        verbose_name = 'Series Title Page Index Page'

    @route(r'^$', name='all_publishers')
    def serve_all_publishers(self, request):
        """Renders all the publishers."""
        publishers = STP.objects.values(
            'publisher_name', 'publisher_name_slug').distinct().order_by(
            'publisher_name')

        return render(request, self.get_template(request),
                      {'self': self, 'publishers': publishers})

    @route(r'^(?P<slug>.*?)/$', name='rubrics')
    def serve_rubrics(self, request, slug):
        """Renders rubrics for publisher."""
        stps = STP.objects.filter(publisher_name_slug=slug)

        return render(request, self.get_template(request),
                      {'self': self, 'stps': stps})

    @route(r'^(?P<pn_slug>.*?)/(?P<r_slug>.*?)/$', name='rubric')
    def serve_rubric(self, request, pn_slug, r_slug):
        """Renders rubric."""
        stp = STP.objects.filter(publisher_name_slug=pn_slug,
                                 rubric_slug=r_slug).first()

        return render(request, self.get_template(request),
                      {'self': self, 'stp': stp})


STPIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]


class Advert(TimeStampedModel):
    publisher = models.ForeignKey(Publisher, blank=True, null=True,
                                  on_delete = models.CASCADE,
                                  related_name='adverts')
    publisher_name = models.CharField(max_length=256)
    publisher_name_slug = models.CharField(max_length=256, editable=False)
    rubric = RichTextField()
    rubric_slug = models.CharField(max_length=256, editable=False)
    pdf = models.ForeignKey(Document, null=True, blank=True,
                            on_delete=models.CASCADE, related_name='+')

    class Meta:
        ordering = ['publisher_name', 'rubric']

    def __unicode__(self):
        return '{0}: {1}'.format(self.publisher_name, self.rubric)

    def __str__(self):
        return self.__unicode__()

    @property
    def url(self):
        index_page = Page.objects.filter(slug='ii').first()
        stp_index_page = index_page.get_children().filter(
            slug='publishers').first()

        return '{0}{1}/{2}/'.format(stp_index_page.url,
                                    self.publisher_name_slug, self.rubric_slug)

    def save(self, *args, **kwargs):
        self.publisher_name_slug = slugify(self.publisher_name)
        self.rubric_slug = slugify(self.rubric)
        super(Advert, self).save(*args, **kwargs)


Advert.panels = [
    FieldPanel('rubric', classname='full title'),
    FieldPanel('publisher_name', classname='full'),
    SnippetChooserPanel('publisher', Publisher),
    DocumentChooserPanel('pdf')
]

register_snippet(Advert)


class AdvertIndexPage(RoutablePageMixin, Page, Introducable):
    class Meta:
        verbose_name = 'Publishers\' Advertisements Index Page'

    @route(r'^$', name='all_publishers')
    def serve_all_publishers(self, request):
        """Renders all the publishers."""
        publishers = Advert.objects.values(
            'publisher_name', 'publisher_name_slug').distinct().order_by(
            'publisher_name')

        return render(request, self.get_template(request),
                      {'self': self, 'publishers': publishers})

    @route(r'^(?P<slug>.*?)/$', name='rubrics')
    def serve_rubrics(self, request, slug):
        """Renders rubrics for publisher."""
        adverts = Advert.objects.filter(publisher_name_slug=slug)

        return render(request, self.get_template(request),
                      {'self': self, 'adverts': adverts})

    @route(r'^(?P<pn_slug>.*?)/(?P<r_slug>.*?)/$', name='rubric')
    def serve_rubric(self, request, pn_slug, r_slug):
        """Renders rubric."""
        advert = Advert.objects.filter(publisher_name_slug=pn_slug,
                                       rubric_slug=r_slug).first()

        return render(request, self.get_template(request),
                      {'self': self, 'advert': advert})


AdvertIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('introduction', classname='full'),
]


class Abbreviation(TimeStampedModel):
    abbreviation = models.CharField(max_length=32, unique=True)
    description = RichTextField()
    slug = models.CharField(max_length=256, editable=False)

    class Meta:
        ordering = ['abbreviation']

    def __unicode__(self):
        return '{0}: {1}'.format(self.abbreviation, self.description)

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.abbreviation)
        super(Abbreviation, self).save(*args, **kwargs)


Abbreviation.panels = [
    FieldPanel('abbreviation', classname='full title'),
    FieldPanel('description', classname='full')
]

register_snippet(Abbreviation)


class AbbreviationIndexPage(RoutablePageMixin, Page, Introducable):

    @route(r'^$', name='all_abbreviations')
    def serve_all_abbreviations(self, request):
        """Renders all the abbreviations."""
        abbreviations = Abbreviation.objects.all()

        return render(request, self.get_template(request),
                      {'self': self, 'abbreviations': abbreviations})


AbbreviationIndexPage.content_panels = [
    FieldPanel('title', classname='title full'),
    FieldPanel('introduction', classname='full')
]


class GlossaryItem(TimeStampedModel):
    title = models.CharField(max_length=32, unique=True)
    description = RichTextField()
    slug = models.CharField(max_length=256, editable=False)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(GlossaryItem, self).save(*args, **kwargs)


GlossaryItem.panels = [
    FieldPanel('title', classname='title full'),
    FieldPanel('description', classname='full')
]

register_snippet(GlossaryItem)


class GlossaryIndexPage(RoutablePageMixin, Page, Introducable):

    @route(r'^$', name='all_glossary_items')
    def serve_all_glossary_items(self, request):
        '''Renders all glossary items.'''
        glossary_items = GlossaryItem.objects.all()
        return render(request, self.get_template(request),
                      {'self': self, 'glossary_items': glossary_items})


GlossaryIndexPage.content_panels = [
    FieldPanel('title', classname='title full'),
    FieldPanel('introduction', classname='full')
]
