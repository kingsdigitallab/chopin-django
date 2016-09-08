from django.contrib.contenttypes.models import ContentType
from haystack import indexes
from models import Impression, Library, Publisher, Work
from wagtail.wagtailcore.models import Page


class ImpressionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Impression')
    title = indexes.CharField(boost=100)
    resource =indexes.FacetMultiValueField(default=["ACO"])
    sort_order = indexes.FloatField()
    url = indexes.CharField(model_attr='url', indexed=False, null=True)

    def get_model(self):
        return Impression

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True)

    def prepare_title(self, impression):
        return u'{0}: {1}'.format(impression.get_parent().title,
                                  impression.title)

    def prepare_sort_order(self, impression):
        work_sort_order = impression.get_parent().work.sort_order
        sort_order = impression.sort_order

        return work_sort_order + (float(sort_order) / 1000)


class LibraryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Library')
    resource =indexes.FacetMultiValueField(default=["ACO"])
    title = indexes.CharField()
    url = indexes.CharField(model_attr='url', indexed=False, null=True)

    def get_model(self):
        return Library

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True)

    def prepare_title(self, library):
        return library.__unicode__()


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Contextual material')
    title = indexes.CharField()
    resource =indexes.FacetMultiValueField(default=["ACO"])
    url = indexes.CharField(model_attr='url', indexed=False, null=True)

    def get_model(self):
        return Page

    def index_queryset(self, using=None):
        content_types = ContentType.objects.filter(
            name__in=['Impression', 'Work'])
        return self.get_model().objects.exclude(
            content_type__in=content_types).filter(live=True)

    def prepare_title(self, page):
        title = page.title
        ancestors = page.get_ancestors()[3:]

        for ancestor in ancestors:
            title = ancestor.title + ' / ' + title

        return title


class PublisherIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    document = indexes.FacetCharField(default='Publisher')
    resource =indexes.FacetMultiValueField(default=["ACO"])
    title = indexes.CharField()
    url = indexes.CharField(model_attr='url', indexed=False, null=True)

    def get_model(self):
        return Publisher

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True)

    def prepare_title(self, publisher):
        return publisher.__unicode__()


class WorkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    document = indexes.FacetCharField(default='General information')
    title = indexes.CharField(model_attr='title')
    resource =indexes.FacetMultiValueField(default=["ACO"])
    sort_order = indexes.FloatField(model_attr='sort_order')
    url = indexes.CharField(model_attr='url', indexed=False, null=True)

    def get_model(self):
        return Work

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(live=True)

    def prepare_text(self, work):
        return work.heading
